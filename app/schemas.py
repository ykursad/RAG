from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int | None = Field(default=None, ge=1, le=20)
    source_filter: str | None = Field(
        default=None,
        description="Yalnızca belirli bir belge kaynağında arama yap"
    )


class SourceChunk(BaseModel):
    chunk_id: str
    score: float | None = None
    page: int | None = None
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    prompt_context_length: int
    retrieved_pages: list[int]
    source_count: int
    retrieved_sources: list[str]


class IngestResponse(BaseModel):
    message: str
    filename: str
    total_chunks: int
    pages: int
    source_name: str


class RetrieveResponse(BaseModel):
    question: str
    results: list[SourceChunk]
    total_results: int


class HealthResponse(BaseModel):
    status: str
    collection_name: str
    indexed_records: int
    ollama_base_url: str
    chat_model: str
    embedding_model: str
    app_env: str


class DocumentSummary(BaseModel):
    source_name: str
    chunk_count: int
    pages: list[int]


class DocumentListResponse(BaseModel):
    total_documents: int
    documents: list[DocumentSummary]