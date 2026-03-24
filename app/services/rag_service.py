from __future__ import annotations

import logging
from pathlib import Path

from app.config import Settings
from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas import SourceChunk
from app.services.chunker import TextChunker
from app.services.document_loader import DocumentLoader
from app.services.ollama_client import OllamaClient
from app.services.vector_store import VectorStore


class RagService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.loader = DocumentLoader()
        self.chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        self.ollama = OllamaClient(settings)
        self.store = VectorStore(settings)
        self.logger = logging.getLogger("rag_service")

    def ingest_document(self, file_path: Path) -> dict:
        self.logger.info("Doküman ingest başladı: %s", file_path.name)

        pages = self.loader.load(file_path)
        source_name = file_path.stem.replace(" ", "_").lower()
        chunks = self.chunker.split_pages(pages, source_name=source_name)

        if not chunks:
            raise ValueError("Belgeden chunk üretilemedi.")

        self.logger.info(
            "Chunk üretildi | dosya=%s | chunk_sayisi=%s",
            file_path.name,
            len(chunks),
        )

        embeddings = self.ollama.embed([chunk.text for chunk in chunks])

        self.logger.info("Embedding üretildi | dosya=%s", file_path.name)

        self.store.reset_collection()
        self.store.add_chunks(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk.metadata for chunk in chunks],
        )

        self.logger.info("Doküman ingest tamamlandı: %s", file_path.name)

        return {
            "filename": file_path.name,
            "total_chunks": len(chunks),
            "pages": len(pages),
            "source_name": source_name,
        }

    def retrieve(self, question: str, top_k: int | None = None) -> list[SourceChunk]:
        top_k = top_k or self.settings.top_k
        self.logger.info("Retrieve başladı | soru=%s | top_k=%s", question, top_k)

        query_embedding = self.ollama.embed([question])[0]
        raw = self.store.query(query_embedding=query_embedding, top_k=top_k)

        ids = raw.get("ids", [[]])[0]
        documents = raw.get("documents", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0]

        results: list[SourceChunk] = []
        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            metadata = metadata or {}
            results.append(
                SourceChunk(
                    chunk_id=chunk_id,
                    score=None if distance is None else float(distance),
                    page=metadata.get("page"),
                    text=document,
                    metadata=metadata,
                )
            )

        results = self._deduplicate_sources(results)
        self.logger.info("Retrieve tamamlandı | sonuc_sayisi=%s", len(results))
        return results

    def _deduplicate_sources(self, results: list[SourceChunk]) -> list[SourceChunk]:
        unique: list[SourceChunk] = []
        seen_keys = set()

        for item in results:
            text_key = item.text[:250].strip().lower()
            key = (item.page, text_key)

            if key in seen_keys:
                continue

            seen_keys.add(key)
            unique.append(item)

        return unique

    def _select_context_chunks(self, retrieved: list[SourceChunk]) -> list[SourceChunk]:
        selected: list[SourceChunk] = []
        seen_pages = set()

        for item in retrieved:
            if len(selected) >= self.settings.max_context_chunks:
                break

            if item.page not in seen_pages:
                selected.append(item)
                seen_pages.add(item.page)

        if len(selected) < self.settings.max_context_chunks:
            for item in retrieved:
                if len(selected) >= self.settings.max_context_chunks:
                    break
                if item not in selected:
                    selected.append(item)

        return selected

    def answer(self, question: str, top_k: int | None = None) -> dict:
        self.logger.info("Answer başladı | soru=%s", question)
        retrieved = self.retrieve(question=question, top_k=top_k)

        if not retrieved:
            return {
                "answer": (
                    "Kısa Cevap:\nİndekste uygun içerik bulunamadı.\n\n"
                    "Detaylı Açıklama:\nÖnce bir doküman yükleyip indeks oluşturmanız gerekiyor.\n\n"
                    "Dokümandaki Dayanaklar:\n- Uygun bağlam bulunamadı.\n\n"
                    "Belirsizlik / Not:\n- Bu cevap herhangi bir doküman bağlamına dayanmıyor.\n\n"
                    "Kaynaklar:\nYok"
                ),
                "sources": [],
                "prompt_context_length": 0,
                "retrieved_pages": [],
                "source_count": 0,
                "retrieved_sources": [],
            }

        selected = self._select_context_chunks(retrieved)

        context_blocks = [
            {"page": item.page, "text": item.text, "score": item.score}
            for item in selected
        ]

        user_prompt = build_user_prompt(question, context_blocks)
        answer = self.ollama.chat(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)

        retrieved_pages = sorted({item.page for item in selected if item.page is not None})
        retrieved_sources = list({item.metadata.get("source") for item in selected if item.metadata.get("source")})

        self.logger.info("Answer tamamlandı | kaynak_sayisi=%s", len(selected))

        return {
            "answer": answer,
            "sources": selected,
            "prompt_context_length": len(user_prompt),
            "retrieved_pages": retrieved_pages,
            "source_count": len(selected),
            "retrieved_sources": retrieved_sources,
        }