
from fastapi import APIRouter, Depends, HTTPException, Header, status
from enums.responses import ResponseSignal
from schemas.chat import ChatRequest, ChatResponse, ClearSessionResponse, HealthResponse
from services.chat_service import ChatService
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


chat_router = APIRouter(
    prefix="/api/v1/chat",
    tags=["chat"],
)


# ------------------------------------------------------------------
# Dependency: ChatService
# This function is called by FastAPI for each request that needs it.
# The ChatService instance is provided by main.py at startup.
# ------------------------------------------------------------------

_chat_service_instance: ChatService | None = None


def get_chat_service() -> ChatService:
   
    if _chat_service_instance is None:
         raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ResponseSignal.SERVICE_UNAVAILABLE.value
        )
    return _chat_service_instance


def set_chat_service(service: ChatService) -> None:
    """
    Called by main.py at startup to inject the ChatService instance.
    """
    global _chat_service_instance
    _chat_service_instance = service
    logger.info("ChatService injected into router.")



def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
    """
    بياخد الـ tenant من الـ header ويتحقق منه.
    """
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

# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@chat_router.post("", response_model=ChatResponse,)
async def chat(
    request: ChatRequest,
    tenant_id: str = Depends(get_tenant_id),
    service: ChatService = Depends(get_chat_service),) -> ChatResponse:
   
    logger.info(f"POST /api/chat | tenant={tenant_id} | session={request.session_id}")

    try:
        result = service.handle_message(
            session_id=request.session_id,
            user_message=request.message,
            tenant_id=tenant_id,
        )

    except RuntimeError as e:
        logger.error(f"Chat error | tenant={tenant_id} | session={request.session_id} | error={e}")
        raise  HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ResponseSignal.LLM_RESPONSE_ERROR.value
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error in chat | tenant={tenant_id} | session={request.session_id} | error={e}")
        raise  HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseSignal.HTTP_500_INTERNAL_SERVER_ERROR.value
        )

    return ChatResponse(
        session_id=result["session_id"],
        reply=result["reply"],
        turn_count=result["turn_count"],
    )


@chat_router.delete(
    "/{session_id}",
    response_model=ClearSessionResponse,
    summary="Clear conversation history for a session",
    description="Deletes the in-memory conversation history for the given session_id.",
)

async def clear_session(
    session_id: str,
    service: ChatService = Depends(get_chat_service),) -> ClearSessionResponse:
   
    logger.info(f"DELETE /api/chat/{session_id}")
    cleared = service.clear_session(session_id)
    return ClearSessionResponse(
        session_id=session_id,
        cleared=cleared,
        message=(
            "Conversation history cleared successfully."
            if cleared
            else "No session found with that ID."
        ),
    )


@chat_router.get(
    "/health",
    response_model=HealthResponse,
    description="Returns the operational status of the service,returns OK if the service is running.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="Medical Platform")
