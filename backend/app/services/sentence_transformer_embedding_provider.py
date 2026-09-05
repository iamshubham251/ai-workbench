"""Sentence Transformers embedding provider."""

from sentence_transformers import SentenceTransformer

from app.models.document_chunk import DocumentChunk
from app.models.embedding import DocumentEmbedding
from app.services.embedding_provider import (
    EmbeddingError,
    EmbeddingProvider,
)


class SentenceTransformerEmbeddingProvider:
    """Generate local embeddings using Sentence Transformers."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        if not model_name.strip():
            raise ValueError("model_name must not be empty")

        try:
            self.model = SentenceTransformer(model_name)
        except Exception as exc:
            raise EmbeddingError(
                f"Embedding model could not be loaded: {model_name}"
            ) from exc

        self.model_name = model_name

    def embed(
        self,
        chunk: DocumentChunk,
    ) -> DocumentEmbedding:
        """Generate an embedding for one document chunk."""
        try:
            vector = self.model.encode(
                chunk.text,
                normalize_embeddings=True,
            )
        except Exception as exc:
            raise EmbeddingError(
                "Embedding generation failed"
            ) from exc

        return DocumentEmbedding(
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            vector=tuple(float(value) for value in vector),
        )

    def embed_batch(
        self,
        chunks: tuple[DocumentChunk, ...],
    ) -> tuple[DocumentEmbedding, ...]:
        """Generate embeddings for multiple document chunks."""
        if not chunks:
            return ()

        try:
            texts = [chunk.text for chunk in chunks]

            vectors = self.model.encode(
                texts,
                normalize_embeddings=True,
            )
        except Exception as exc:
            raise EmbeddingError(
                "Batch embedding generation failed"
            ) from exc

        return tuple(
            DocumentEmbedding(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                vector=tuple(float(value) for value in vector),
            )
            for chunk, vector in zip(chunks, vectors)
        )


assert issubclass(
    SentenceTransformerEmbeddingProvider,
    object,
)
