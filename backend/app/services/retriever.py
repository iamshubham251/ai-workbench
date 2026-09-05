"""Semantic retrieval over persisted document embeddings."""

from dataclasses import dataclass
from uuid import UUID

from app.models.document_chunk import DocumentChunk
from app.models.embedding import DocumentEmbedding
from app.services.vector_similarity import cosine_similarity


@dataclass(frozen=True)
class RetrievalResult:
    document_id: UUID
    chunk_index: int
    text: str
    score: float
    page_numbers: tuple[int, ...] = ()
    section_title: str | None = None


class Retriever:
    """Rank document chunks by cosine similarity."""

    def retrieve(
        self,
        query_embedding: tuple[float, ...],
        chunks: tuple[DocumentChunk, ...],
        embeddings: tuple[DocumentEmbedding, ...],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> tuple[RetrievalResult, ...]:
        """Return the most relevant chunks above the minimum score."""

        if top_k < 1:
            raise ValueError("top_k must be positive")

        if not 0.0 <= min_score <= 1.0:
            raise ValueError("min_score must be between 0.0 and 1.0")

        chunk_map = {
            chunk.chunk_index: chunk
            for chunk in chunks
        }

        results: list[RetrievalResult] = []

        for embedding in embeddings:
            chunk = chunk_map.get(embedding.chunk_index)

            if chunk is None:
                continue

            score = cosine_similarity(
                query_embedding,
                embedding.vector,
            )

            if score < min_score:
                continue

            results.append(
                RetrievalResult(
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    score=score,
                    page_numbers=chunk.page_numbers,
                    section_title=chunk.section_title,
                )
            )

        results.sort(
            key=lambda result: (-result.score, result.chunk_index),
        )

        return tuple(results[:top_k])
