from pathlib import Path


class FileValidator:
    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
    MAX_FILE_SIZE_MB = 10

    @classmethod
    def validate_extension(cls, filename: str) -> None:
        suffix = Path(filename).suffix.lower()
        if suffix not in cls.ALLOWED_EXTENSIONS:
            raise ValueError("Yalnızca PDF, TXT ve MD yükleyebilirsiniz.")

    @classmethod
    def validate_size(cls, content: bytes) -> None:
        size_mb = len(content) / (1024 * 1024)
        if size_mb > cls.MAX_FILE_SIZE_MB:
            raise ValueError(f"Dosya boyutu {cls.MAX_FILE_SIZE_MB} MB sınırını aşıyor.")

    @classmethod
    def validate_filename(cls, filename: str | None) -> None:
        if not filename or not filename.strip():
            raise ValueError("Geçerli bir dosya adı bulunamadı.")