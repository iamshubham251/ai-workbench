"""Generate embeddings for user search queries."""

from app.services.embedding_provider import EmbeddingError
from app.services.sentence_transformer_embedding_provider import (
    SentenceTransformerEmbeddingProvider,
)


class QueryEmbeddingService:
    """Convert natural-language queries into embedding vectors."""

    def __init__(
        self,
        provider: SentenceTransformerEmbeddingProvider | None = None,
    ) -> None:
        self.provider = provider or SentenceTransformerEmbeddingProvider()

    def embed_query(self, query: str) -> tuple[float, ...]:
        """Generate a normalized embedding for a user query."""

        if not query.strip():
            raise ValueError("query must not be empty")

        try:
            vector = self.provider.model.encode(
                query,
                normalize_embeddings=True,
            )
        except Exception as exc:
            raise EmbeddingError(
                "Query embedding generation failed"
            ) from exc

        return tuple(float(value) for value in vector)
