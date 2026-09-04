"""Repository for storing and retrieving document chunks."""

from uuid import UUID

from app.models.document_chunk import DocumentChunk


class ChunkRepository:
    """In-memory repository for document chunks."""

    def __init__(self) -> None:
        self._chunks: dict[UUID, tuple[DocumentChunk, ...]] = {}

    def save(
        self,
        document_id: UUID,
        chunks: tuple[DocumentChunk, ...],
    ) -> None:
        """Store chunks for a document."""
        self._chunks[document_id] = chunks

    def get_by_document_id(
        self,
        document_id: UUID,
    ) -> tuple[DocumentChunk, ...]:
        """Return all chunks belonging to a document."""
        return self._chunks.get(document_id, ())

    def delete_by_document_id(
        self,
        document_id: UUID,
    ) -> None:
        """Delete all chunks belonging to a document."""
        self._chunks.pop(document_id, None)

    def count_by_document_id(
        self,
        document_id: UUID,
    ) -> int:
        """Return the number of chunks stored for a document."""
        return len(self.get_by_document_id(document_id))