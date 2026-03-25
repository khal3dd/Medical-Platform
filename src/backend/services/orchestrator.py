from core.logger import get_logger
from providers.embeddings import EmbeddingsProvider
from providers.vector_store import VectorStore
from services.chat_service import ChatService

logger = get_logger(__name__)


class Orchestrator:

    def __init__(
        self,
        embeddings_provider: EmbeddingsProvider,
        vector_store: VectorStore,
        chat_service: ChatService,
    ) -> None:
        self._embeddings = embeddings_provider
        self._vector_store = vector_store
        self._chat_service = chat_service
        logger.info("Orchestrator initialized.")

    def handle_message(
        self,
        session_id: str,
        user_message: str,
        tenant_id: str,
    ) -> dict:

        logger.info(f"Retrieving context | tenant={tenant_id} | session={session_id}")

        try:
            query_vector = self._embeddings.embed_one(user_message)
            chunks = self._vector_store.query(
                query_vector=query_vector,
                tenant_id=tenant_id,
            )
        except Exception as e:
            logger.error(f"Retrieval failed | tenant={tenant_id} | session={session_id} | error={e}")
            raise RuntimeError(f"Retrieval failed: {e}") from e

        context = self._build_context(chunks)

        logger.info(f"Context built | tenant={tenant_id} | session={session_id} | chunks={len(chunks)}")

        result = self._chat_service.handle_message(
            session_id=session_id,
            user_message=user_message,
            context=context if chunks else None,
        )

        result["retrieved_chunks"] = len(chunks)
        return result

    def _build_context(self, chunks: list[str]) -> str:
        if not chunks:
            return ""
        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(f"[{i}] {chunk}")
        return "\n\n".join(parts)