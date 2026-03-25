from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, status
from core.config import settings
from core.logger import get_logger
from enums.responses import ResponseSignal
from services.ingestion_service import IngestionService

logger = get_logger(__name__)

ingestion_router = APIRouter(
    prefix="/api/v1/ingestion",
    tags=["ingestion"],
)

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


def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header is required.",
        )
    if x_tenant_id not in settings.allowed_tenants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown tenant: '{x_tenant_id}'. Allowed: {settings.allowed_tenants}",
        )
    return x_tenant_id


@ingestion_router.post("/upload", summary="Uploading and adding the PDF to the Vector Store")
async def upload_pdf(
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_tenant_id),
    service: IngestionService = Depends(get_ingestion_service),
) -> dict:

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value,
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"File saved | tenant={tenant_id} | path={file_path}")
    except Exception as e:
        logger.error(f"File save failed | tenant={tenant_id} | error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseSignal.FILE_UPLOAD_FAILED.value,
        )

    try:
        result = service.ingest_pdf(str(file_path), tenant_id)
    except ValueError:
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
        "tenant_id": tenant_id,
        "file_name": result["file_name"],
        "chunks_count": result["chunks_count"],
        "status": result["status"],
    }


@ingestion_router.delete(
    "/document/{file_name}",
    summary="Delete a specific document from the Vector Store",
)
async def delete_document(
    file_name: str,
    tenant_id: str = Depends(get_tenant_id),
    service: IngestionService = Depends(get_ingestion_service),
) -> dict:
    deleted = service.delete_document(file_name, tenant_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{file_name}' not found for tenant '{tenant_id}'.",
        )
    return {"status": "success", "message": f"Document '{file_name}' deleted from tenant '{tenant_id}'."}


@ingestion_router.get("/status", summary="Number of chunks in Vector Store for tenant")
async def vector_store_status(
    tenant_id: str = Depends(get_tenant_id),
    service: IngestionService = Depends(get_ingestion_service),
) -> dict:
    return {
        "tenant_id": tenant_id,
        "chunks_in_store": service.get_chunks_count(tenant_id),
    }