
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
        self._collection = self._client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"VectorStore initialized | "
            f"collection={settings.collection_name} | "
            f"documents={self._collection.count()}"
        )

    def add_chunks(
        self,
        chunks: list[str],
        vectors: list[list[float]],
        source_file: str,
    ) -> int:
       
        if not chunks:
            return 0

        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{"source": source_file, "chunk_index": i} for i in range(len(chunks))]

        self._collection.add(
            ids=ids,
            embeddings=vectors,
            documents=chunks,
            metadatas=metadatas,
        )

        logger.info(
            f"Chunks added | file={source_file} | count={len(chunks)}"
        )
        return len(chunks)

    def query(
        self,
        query_vector: list[float],
        top_k: int | None = None,
    ) -> list[str]:
       
        k = top_k or settings.retrieval_top_k

        if self._collection.count() == 0:
            logger.warning("Query on empty collection — no documents uploaded yet.")
            return []

        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=min(k, self._collection.count()),
        )

        documents = results.get("documents", [[]])[0]
        logger.debug(f"Retrieved {len(documents)} chunks for query")
        return documents

    def count(self) -> int:
        return self._collection.count()
    


    def delete_by_source(self, source_file: str) -> bool:
     results = self._collection.get( where={"source": source_file} )

     ids = results.get("ids", [])

     if not ids:
         logger.warning(f"No chunks found for source: {source_file}")
         return False
     self._collection.delete(ids=ids)
     logger.info(f"Deleted {len(ids)} chunks | source={source_file}")
     return True