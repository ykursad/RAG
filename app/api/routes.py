from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import Settings, get_settings
from app.schemas import (
    AskRequest,
    AskResponse,
    DocumentListResponse,
    DocumentSummary,
    HealthResponse,
    IngestResponse,
    RetrieveResponse,
)
from app.services.file_validation import FileValidator
from app.services.rag_service import RagService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_service(settings: Settings = Depends(get_settings)) -> RagService:
    return RagService(settings)


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "title": "Şükrü Yusuf KAYA - Çok Dokümanlı RAG Asistanı",
        },
    )


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(get_settings),
    service: RagService = Depends(get_service),
):
    return HealthResponse(
        status="ok" if service.ollama.healthcheck() else "degraded",
        collection_name=settings.chroma_collection,
        indexed_records=service.store.count(),
        ollama_base_url=settings.ollama_base_url,
        chat_model=settings.ollama_chat_model,
        embedding_model=settings.ollama_embed_model,
        app_env=settings.app_env,
    )


@router.post("/reset")
def reset_index(service: RagService = Depends(get_service)):
    try:
        service.store.reset_collection()
        return {"message": "İndeks başarıyla sıfırlandı."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/documents", response_model=DocumentListResponse)
def list_documents(service: RagService = Depends(get_service)):
    try:
        docs = service.list_documents()
        return DocumentListResponse(
            total_documents=len(docs),
            documents=[DocumentSummary(**doc) for doc in docs],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/documents/{source_name}")
def delete_document(
    source_name: str,
    service: RagService = Depends(get_service),
):
    try:
        service.delete_document(source_name=source_name)
        return {"message": f"{source_name} kaynağı silindi."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ingest", response_model=IngestResponse)
def ingest_document(
    file: UploadFile = File(...),
    service: RagService = Depends(get_service),
):
    try:
        FileValidator.validate_filename(file.filename)
        FileValidator.validate_extension(file.filename or "")
        file_bytes = file.file.read()
        FileValidator.validate_size(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / (file.filename or "uploaded_file")
    file_path.write_bytes(file_bytes)

    try:
        result = service.ingest_document(file_path=file_path)
        return IngestResponse(
            message="Doküman başarıyla işlendi ve indekslendi.",
            filename=result["filename"],
            total_chunks=result["total_chunks"],
            pages=result["pages"],
            source_name=result["source_name"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_only(
    payload: AskRequest,
    service: RagService = Depends(get_service),
):
    try:
        results = service.retrieve(
            question=payload.question,
            top_k=payload.top_k,
            source_filter=payload.source_filter,
        )
        return RetrieveResponse(
            question=payload.question,
            results=results,
            total_results=len(results),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ask", response_model=AskResponse)
def ask_question(
    payload: AskRequest,
    service: RagService = Depends(get_service),
):
    try:
        result = service.answer(
            question=payload.question,
            top_k=payload.top_k,
            source_filter=payload.source_filter,
        )
        return AskResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc