from sentence_transformers import SentenceTransformer
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


class EmbeddingsProvider:
 

    def __init__(self) -> None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self._model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully ✅")

    def embed(self, texts: list[str]) -> list[list[float]]:
      
        if not texts:
            return []

        logger.debug(f"Embedding {len(texts)} texts...")
        vectors = self._model.encode(texts, show_progress_bar=False)
        logger.debug(f"Embedding done | shape={vectors.shape}")

        return vectors.tolist()

    def embed_one(self, text: str) -> list[float]:
     
        return self.embed([text])[0]