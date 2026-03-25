import uuid
import chromadb
from chromadb.config import Settings as ChromaSettings
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


class VectorStore:

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=settings.vector_store_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info("VectorStore initialized.")

    def _get_collection(self, tenant_id: str):
        
        return self._client.get_or_create_collection(
            name=tenant_id,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        chunks: list[str],
        vectors: list[list[float]],
        source_file: str,
        tenant_id: str,
    ) -> int:
        collection = self._get_collection(tenant_id)
        if not chunks:
            return 0

        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{"source": source_file, "chunk_index": i} for i in range(len(chunks))]

        collection.add(
            ids=ids,
            embeddings=vectors,
            documents=chunks,
            metadatas=metadatas,
        )

        logger.info(f"Chunks added | tenant={tenant_id} | file={source_file} | count={len(chunks)}")
        return len(chunks)

    def query(
        self,
        query_vector: list[float],
        tenant_id: str,
        top_k: int | None = None,
    ) -> list[str]:
        collection = self._get_collection(tenant_id)
        k = top_k or settings.retrieval_top_k

        if collection.count() == 0:
            logger.warning(f"Empty collection | tenant={tenant_id}")
            return []

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=min(k, collection.count()),
        )

        documents = results.get("documents", [[]])[0]
        logger.debug(f"Retrieved {len(documents)} chunks | tenant={tenant_id}")
        return documents

    def delete_by_source(self, source_file: str, tenant_id: str) -> bool:
        collection = self._get_collection(tenant_id)
        results = collection.get(where={"source": source_file})
        ids = results.get("ids", [])

        if not ids:
            logger.warning(f"No chunks found | tenant={tenant_id} | file={source_file}")
            return False

        collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} chunks | tenant={tenant_id} | file={source_file}")
        return True

    def count(self, tenant_id: str) -> int:
        collection = self._get_collection(tenant_id)
        return collection.count()