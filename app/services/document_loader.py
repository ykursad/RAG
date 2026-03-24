from pathlib import Path

from pypdf import PdfReader


class DocumentLoader:
    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

    def load(self, file_path: Path) -> list[dict]:
        suffix = file_path.suffix.lower()

        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Desteklenmeyen dosya türü: {suffix}")

        if suffix == ".pdf":
            return self._load_pdf(file_path)

        return self._load_text(file_path)

    def _load_pdf(self, file_path: Path) -> list[dict]:
        reader = PdfReader(str(file_path))
        pages: list[dict] = []

        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            normalized = self._normalize_text(text)

            if normalized:
                pages.append({
                    "page": index,
                    "text": normalized
                })

        if not pages:
            raise ValueError("PDF içerisinden metin çıkarılamadı. Belge taranmış olabilir.")

        return pages

    def _load_text(self, file_path: Path) -> list[dict]:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        normalized = self._normalize_text(text)

        if not normalized:
            raise ValueError("Dosya boş veya okunabilir metin içermiyor.")

        return [{
            "page": 1,
            "text": normalized
        }]

    @staticmethod
    def _normalize_text(text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        filtered = [line for line in lines if line]
        return "\n".join(filtered).strip()