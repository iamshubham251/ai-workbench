"""Core local RAG retrieval and grounded answer service."""

from dataclasses import dataclass
from uuid import UUID

from app.models.document_chunk import DocumentChunk
from app.models.embedding import DocumentEmbedding
from app.repositories.chunk_sql_repository import SqlChunkRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.answer_generator import AnswerGenerator
from app.services.query_embedding_service import QueryEmbeddingService
from app.services.retriever import RetrievalResult, Retriever


@dataclass(frozen=True)
class RagResponse:
    """Relevant knowledge and grounded answer for a user query."""

    query: str
    answer: str
    results: tuple[RetrievalResult, ...]

    @property
    def result_count(self) -> int:
        return len(self.results)


class RagService:
    """Connect query embedding, semantic retrieval, and answer generation."""

    DEFAULT_MIN_SCORE = 0.35

    def __init__(
        self,
        chunk_repository: SqlChunkRepository,
        embedding_repository: EmbeddingRepository,
        query_embedding_service: QueryEmbeddingService,
        answer_generator: AnswerGenerator,
        retriever: Retriever | None = None,
        min_score: float = DEFAULT_MIN_SCORE,
    ) -> None:
        if not 0.0 <= min_score <= 1.0:
            raise ValueError(
                "min_score must be between 0.0 and 1.0"
            )

        self.chunk_repository = chunk_repository
        self.embedding_repository = embedding_repository
        self.query_embedding_service = query_embedding_service
        self.answer_generator = answer_generator
        self.retriever = retriever or Retriever()
        self.min_score = min_score

    def query(
        self,
        document_id: UUID,
        query: str,
        top_k: int = 5,
    ) -> RagResponse:
        """Retrieve evidence and generate a grounded answer."""

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
                answer="No supporting evidence was found for this query.",
                results=(),
            )

        query_vector = self.query_embedding_service.embed_query(query)

        results = self.retriever.retrieve(
            query_embedding=query_vector,
            chunks=chunks,
            embeddings=embeddings,
            top_k=top_k,
            min_score=self.min_score,
        )

        if not results:
            return RagResponse(
                query=query,
                answer="No supporting evidence was found for this query.",
                results=(),
            )

        answer = self.answer_generator.generate(
            query=query,
            results=results,
        )

        return RagResponse(
            query=query,
            answer=answer,
            results=results,
        )

    def query_all(
        self,
        query: str,
        top_k: int = 5,
    ) -> RagResponse:
        """Retrieve evidence across all indexed documents."""

        if not query.strip():
            raise ValueError("query must not be empty")

        chunks = self.chunk_repository.get_all()
        embeddings = self.embedding_repository.get_all()

        if not chunks or not embeddings:
            return RagResponse(
                query=query,
                answer="No supporting evidence was found for this query.",
                results=(),
            )

        query_vector = self.query_embedding_service.embed_query(query)

        results = self.retriever.retrieve(
            query_embedding=query_vector,
            chunks=chunks,
            embeddings=embeddings,
            top_k=top_k,
            min_score=self.min_score,
        )

        if not results:
            return RagResponse(
                query=query,
                answer="No supporting evidence was found for this query.",
                results=(),
            )

        answer = self.answer_generator.generate(
            query=query,
            results=results,
        )

        return RagResponse(
            query=query,
            answer=answer,
            results=results,
        )
