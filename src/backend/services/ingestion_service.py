
from pathlib import Path
from core.logger import get_logger
from providers.embeddings import EmbeddingsProvider
from providers.vector_store import VectorStore
from utils.pdf_processor import process_pdf

logger = get_logger(__name__)


class IngestionService:

    def __init__(
        self,
        embeddings_provider: EmbeddingsProvider,
        vector_store: VectorStore,
    ) -> None:
        self._embeddings = embeddings_provider
        self._vector_store = vector_store
        logger.info("IngestionService initialized.")

    def ingest_pdf(self, pdf_path: str) -> dict:
       
        file_name = Path(pdf_path).name
        logger.info(f"Starting ingestion | file={file_name}")

        try:
            chunks = process_pdf(pdf_path)

        except (FileNotFoundError, ValueError) as e:
            logger.error(f"PDF processing failed | file={file_name} | error={e}")
            raise

        
        try:
            vectors = self._embeddings.embed(chunks)

        except Exception as e:
            logger.error(f"Embedding failed | file={file_name} | error={e}")
            raise RuntimeError(f"Embedding failed: {e}") from e

      
        try:
            count = self._vector_store.add_chunks(
                chunks=chunks,
                vectors=vectors,
                source_file=file_name,
            )
        except Exception as e:
            logger.error(f"Vector store save failed | file={file_name} | error={e}")
            raise RuntimeError(f"Vector store failed: {e}") from e

        logger.info(f"Ingestion complete | file={file_name} | chunks={count}")

        return {
            "file_name": file_name,
            "chunks_count": count,
            "status": "success",
        }
    
    def get_chunks_count(self) -> int:
        return self._vector_store.count()
    
    
    def delete_document(self, file_name: str) -> bool:
     return self._vector_store.delete_by_source(file_name)
    