"""Domain types for embedding generation."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DocumentEmbedding:
    """An embedding vector associated with a document chunk."""

    document_id: UUID
    chunk_index: int
    vector: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.chunk_index < 0:
            raise ValueError("chunk_index must not be negative")

        if not self.vector:
            raise ValueError("vector must not be empty")

        if not all(
            isinstance(value, (int, float))
            for value in self.vector
        ):
            raise ValueError("vector values must be numeric")

    @property
    def dimensions(self) -> int:
        """Return the number of dimensions in the embedding."""
        return len(self.vector)
