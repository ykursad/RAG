from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    text: str
    page: int
    metadata: dict


class TextChunker:
    def __init__(self, chunk_size: int = 1100, chunk_overlap: int = 180):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap, chunk_size değerinden küçük olmalıdır.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_pages(self, pages: list[dict], source_name: str) -> list[Chunk]:
        chunks: list[Chunk] = []

        for page_item in pages:
            page_number = int(page_item["page"])
            text = page_item["text"]

            page_chunks = self._split_text(text)

            for index, chunk_text in enumerate(page_chunks):
                chunk_id = f"{source_name}-p{page_number}-c{index}"
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        text=chunk_text,
                        page=page_number,
                        metadata={
                            "source": source_name,
                            "page": page_number,
                            "chunk_index": index,
                        },
                    )
                )

        return chunks

    def _split_text(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            candidate = text[start:end]

            if end < text_length:
                split_at = max(
                    candidate.rfind("\n\n"),
                    candidate.rfind(". "),
                    candidate.rfind("\n"),
                    candidate.rfind(" "),
                )

                if split_at > int(self.chunk_size * 0.6):
                    end = start + split_at + 1
                    candidate = text[start:end]

            cleaned = candidate.strip()
            if cleaned:
                chunks.append(cleaned)

            if end >= text_length:
                break

            start = max(0, end - self.chunk_overlap)

        return chunks