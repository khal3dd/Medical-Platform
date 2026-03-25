from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.config import settings
from core.logger import get_logger
from providers.llm_provider import LLMProvider
from providers.embeddings import EmbeddingsProvider
from providers.vector_store import VectorStore
from services.chat_service import ChatService
from services.ingestion_service import IngestionService
from services.orchestrator import Orchestrator
from routers.chat import chat_router, set_chat_service
from routers.ingestion import ingestion_router, set_ingestion_service

logger = get_logger(__name__)

_FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Medical Platform starting up ===")
    logger.info(f"Model: {settings.llm_model}")
    logger.info(f"Max tokens: {settings.llm_max_tokens}")
    logger.info(f"Temperature: {settings.llm_temperature}")
    logger.info(f"Session max turns: {settings.session_max_turns}")
    logger.info(f"Embedding model: {settings.embedding_model}")
    logger.info(f"Allowed tenants: {settings.allowed_tenants}")
    logger.info(f"Frontend served from: {_FRONTEND_DIR}")

    # Providers
    llm_provider        = LLMProvider()
    embeddings_provider = EmbeddingsProvider()
    vector_store        = VectorStore()

    # Services
    chat_service      = ChatService(llm_provider=llm_provider)
    ingestion_service = IngestionService(
        embeddings_provider=embeddings_provider,
        vector_store=vector_store,
    )
    orchestrator = Orchestrator(
        embeddings_provider=embeddings_provider,
        vector_store=vector_store,
        chat_service=chat_service,
    )

    # Inject into routers
    set_chat_service(orchestrator)
    set_ingestion_service(ingestion_service)

    logger.info("=== All components initialized. Ready at http://localhost:8000 ===")

    yield

    logger.info("=== Medical Platform shutting down ===")


app = FastAPI(
    title="Medical Platform API",
    description=(
        "A safe, educational AI platform that helps patients across multiple "
        "medical departments with general health information and lifestyle guidance. "
        "Not a diagnostic tool. Not a replacement for medical advice."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(ingestion_router)

app.mount("/static", StaticFiles(directory=str(_FRONTEND_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(str(_FRONTEND_DIR / "index.html"))