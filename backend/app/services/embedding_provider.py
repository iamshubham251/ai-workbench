"""Embedding provider interface."""

from typing import Protocol

from app.models.document_chunk import DocumentChunk
from app.models.embedding import DocumentEmbedding


class EmbeddingError(RuntimeError):
    """Raised when embedding generation cannot be completed."""


class EmbeddingProvider(Protocol):
    """Interface implemented by concrete embedding providers."""

    def embed(
        self,
        chunk: DocumentChunk,
    ) -> DocumentEmbedding:
        """Generate an embedding for one document chunk."""
        ...

    def embed_batch(
        self,
        chunks: tuple[DocumentChunk, ...],
    ) -> tuple[DocumentEmbedding, ...]:
        """Generate embeddings for multiple document chunks."""
        ...
