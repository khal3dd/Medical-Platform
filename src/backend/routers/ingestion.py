"""
Ingestion Router — استقبال الـ PDF ورفعه للـ Vector Store.
"""

import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from core.config import settings
from core.logger import get_logger
from enums.responses import ResponseSignal
from services.ingestion_service import IngestionService

logger = get_logger(__name__)

ingestion_router = APIRouter(
    prefix="/api/v1/ingestion",
    tags=["ingestion"],
)

# ------------------------------------------------------------------
# Dependency: IngestionService
# ------------------------------------------------------------------

_ingestion_service_instance: IngestionService | None = None


def get_ingestion_service() -> IngestionService:
    if _ingestion_service_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ResponseSignal.SERVICE_UNAVAILABLE.value,
        )
    return _ingestion_service_instance


def set_ingestion_service(service: IngestionService) -> None:
    global _ingestion_service_instance
    _ingestion_service_instance = service
    logger.info("IngestionService injected into router.")


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@ingestion_router.post(
    "/upload",
    summary="رفع PDF وإضافته للـ Vector Store",
)
async def upload_pdf(
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
) -> dict:

    # تحقق إن الملف PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value,
        )

    # احفظ الملف على الـ disk مؤقتاً
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"File saved | path={file_path}")
    except Exception as e:
        logger.error(f"File save failed | error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseSignal.FILE_UPLOAD_FAILED.value,
        )

    # ابعت للـ IngestionService
    try:
        result = service.ingest_pdf(str(file_path))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.FILE_EMPTY.value,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ResponseSignal.LLM_RESPONSE_ERROR.value,
        )

    return {
        "file_name": result["file_name"],
        "chunks_count": result["chunks_count"],
        "status": result["status"],
    }


@ingestion_router.get(
    "/status",
    summary="عدد الـ documents المحفوظة في الـ Vector Store",
)
async def vector_store_status(
    service: IngestionService = Depends(get_ingestion_service),
) -> dict:
    return {
        "chunks_in_store": service.get_chunks_count(),
    }


@ingestion_router.delete(
    "/document/{file_name}",
    summary="مسح document معين من الـ Vector Store",
)
async def delete_document(
    file_name: str,
    service: IngestionService = Depends(get_ingestion_service),
) -> dict:
    deleted = service.delete_document(file_name)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{file_name}' not found in vector store.",
        )
    return {"status": "success", "message": f"Document '{file_name}' deleted."}    