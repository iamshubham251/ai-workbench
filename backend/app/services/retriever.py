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
    ) -> tuple[RetrievalResult, ...]:
        if top_k < 1:
            raise ValueError("top_k must be positive")

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
            key=lambda result: result.score,
            reverse=True,
        )

        return tuple(results[:top_k])
