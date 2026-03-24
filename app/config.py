from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Single Document RAG UI"
    app_env: str = "dev"

    ollama_base_url: str = "http://localhost:11434/api"
    ollama_chat_model: str = "gemma3:4b"
    ollama_embed_model: str = "embeddinggemma"

    chroma_path: str = "./data/chroma"
    chroma_collection: str = "single_doc_rag"

    top_k: int = 6
    chunk_size: int = 1100
    chunk_overlap: int = 180
    max_context_chunks: int = 5

    hybrid_vector_weight: float = 0.7
    hybrid_lexical_weight: float = 0.3
    rerank_enabled: bool = True
    abstain_if_no_strong_context: bool = True
    max_acceptable_distance: float = 1.2
    min_context_results: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def chroma_dir(self) -> Path:
        return Path(self.chroma_path).resolve()


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return settings