"""Core local RAG retrieval service."""

from dataclasses import dataclass
from uuid import UUID

from app.models.document_chunk import DocumentChunk
from app.models.embedding import DocumentEmbedding
from app.repositories.chunk_sql_repository import SqlChunkRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.query_embedding_service import QueryEmbeddingService
from app.services.retriever import RetrievalResult, Retriever


@dataclass(frozen=True)
class RagResponse:
    """Relevant knowledge returned for a user query."""

    query: str
    results: tuple[RetrievalResult, ...]

    @property
    def result_count(self) -> int:
        return len(self.results)


class RagService:
    """Connect query embedding, persistence, and semantic retrieval."""

    def __init__(
        self,
        chunk_repository: SqlChunkRepository,
        embedding_repository: EmbeddingRepository,
        query_embedding_service: QueryEmbeddingService,
        retriever: Retriever | None = None,
    ) -> None:
        self.chunk_repository = chunk_repository
        self.embedding_repository = embedding_repository
        self.query_embedding_service = query_embedding_service
        self.retriever = retriever or Retriever()

    def query(
        self,
        document_id: UUID,
        query: str,
        top_k: int = 5,
    ) -> RagResponse:
        """Retrieve the most relevant chunks for a query."""

        if not query.strip():
            raise ValueError("query must not be empty")

        chunks: tuple[DocumentChunk, ...] = (
            self.chunk_repository.get_by_document_id(document_id)
        )

        embeddings: tuple[DocumentEmbedding, ...] = (
            self.embedding_repository.get_by_document_id(document_id)
        )

        if not chunks or not embeddings:
            return RagResponse(
                query=query,
                results=(),
            )

        query_vector = self.query_embedding_service.embed_query(query)

        results = self.retriever.retrieve(
            query_embedding=query_vector,
            chunks=chunks,
            embeddings=embeddings,
            top_k=top_k,
        )

        return RagResponse(
            query=query,
            results=results,
        )
