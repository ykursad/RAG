from __future__ import annotations

from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from app.config import Settings


class VectorStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = chromadb.PersistentClient(path=str(settings.chroma_dir))

    def get_collection(self) -> Collection:
        return self.client.get_or_create_collection(name=self.settings.chroma_collection)

    def reset_collection(self) -> None:
        try:
            self.client.delete_collection(name=self.settings.chroma_collection)
        except Exception:
            pass
        self.client.get_or_create_collection(name=self.settings.chroma_collection)

    def delete_by_source(self, source_name: str) -> None:
        collection = self.get_collection()
        collection.delete(where={"source": source_name})

    def add_chunks(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        collection = self.get_collection()
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 4,
        source_filter: str | None = None,
    ) -> dict[str, Any]:
        collection = self.get_collection()

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }

        if source_filter:
            kwargs["where"] = {"source": source_filter}

        return collection.query(**kwargs)

    def fetch_for_lexical_search(
        self,
        source_filter: str | None = None,
    ) -> dict[str, Any]:
        collection = self.get_collection()

        kwargs = {
            "include": ["documents", "metadatas"],
        }

        if source_filter:
            kwargs["where"] = {"source": source_filter}

        return collection.get(**kwargs)

    def count(self) -> int:
        return self.get_collection().count()

    def get_all_metadata(self) -> list[dict[str, Any]]:
        collection = self.get_collection()
        data = collection.get(include=["metadatas"])
        return data.get("metadatas", [])

    def list_documents(self) -> list[dict[str, Any]]:
        metadatas = self.get_all_metadata()

        grouped: dict[str, dict[str, Any]] = {}

        for meta in metadatas:
            if not meta:
                continue

            source = meta.get("source")
            page = meta.get("page")

            if not source:
                continue

            if source not in grouped:
                grouped[source] = {
                    "source_name": source,
                    "chunk_count": 0,
                    "pages": set(),
                }

            grouped[source]["chunk_count"] += 1
            if page is not None:
                grouped[source]["pages"].add(page)

        results: list[dict[str, Any]] = []
        for item in grouped.values():
            results.append(
                {
                    "source_name": item["source_name"],
                    "chunk_count": item["chunk_count"],
                    "pages": sorted(item["pages"]),
                }
            )

        results.sort(key=lambda x: x["source_name"])
        return results