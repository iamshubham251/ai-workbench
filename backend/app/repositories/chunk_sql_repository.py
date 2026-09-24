"""SQLAlchemy repository for persistent document chunks."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.database import get_connection
from app.models.document_chunk import DocumentChunk


class SqlChunkRepository:
    """Persist and retrieve document chunks using SQLAlchemy."""

    def __init__(self, connection=None) -> None:
        # We optionally accept connection to match previous signature,
        # but in SQLAlchemy we usually open short-lived connections.
        self._create_table()

    def _get_connection(self) -> Connection:
        return get_connection()

    def _create_table(self) -> None:
        """Create the document chunks table if it does not exist."""
        with self._get_connection() as conn:
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    document_id VARCHAR(36) NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    page_numbers TEXT NOT NULL,
                    section_title TEXT,
                    PRIMARY KEY (document_id, chunk_index)
                )
                """)
            )
            conn.commit()

    def save(
        self,
        document_id: UUID,
        chunks: tuple[DocumentChunk, ...],
    ) -> None:
        """Replace all stored chunks for a document."""
        self.delete_by_document_id(document_id)

        if not chunks:
            return

        with self._get_connection() as conn:
            conn.execute(
                text("""
                INSERT INTO document_chunks (
                    document_id,
                    chunk_index,
                    text,
                    page_numbers,
                    section_title
                )
                VALUES (
                    :document_id, :chunk_index, :text, :page_numbers, :section_title
                )
                """),
                [
                    {
                        "document_id": str(document_id),
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text,
                        "page_numbers": ",".join(
                            str(page) for page in chunk.page_numbers
                        ),
                        "section_title": chunk.section_title,
                    }
                    for chunk in chunks
                ],
            )
            conn.commit()

    def get_by_document_id(
        self,
        document_id: UUID,
    ) -> tuple[DocumentChunk, ...]:
        """Return all chunks for a document in chunk order."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                text("""
                SELECT
                    chunk_index,
                    text,
                    page_numbers,
                    section_title
                FROM document_chunks
                WHERE document_id = :document_id
                ORDER BY chunk_index ASC
                """),
                {"document_id": str(document_id)},
            )
            rows = cursor.fetchall()

        return tuple(
            DocumentChunk(
                document_id=document_id,
                chunk_index=row._mapping["chunk_index"],
                text=row._mapping["text"],
                page_numbers=tuple(
                    int(page)
                    for page in row._mapping["page_numbers"].split(",")
                    if page
                ),
                section_title=row._mapping["section_title"],
            )
            for row in rows
        )

    def get_all(self) -> tuple[DocumentChunk, ...]:
        """Return all stored chunks in stable document and chunk order."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                text("""
                SELECT
                    document_id,
                    chunk_index,
                    text,
                    page_numbers,
                    section_title
                FROM document_chunks
                ORDER BY document_id ASC, chunk_index ASC
                """)
            )
            rows = cursor.fetchall()

        return tuple(
            DocumentChunk(
                document_id=UUID(row._mapping["document_id"]),
                chunk_index=row._mapping["chunk_index"],
                text=row._mapping["text"],
                page_numbers=tuple(
                    int(page)
                    for page in row._mapping["page_numbers"].split(",")
                    if page
                ),
                section_title=row._mapping["section_title"],
            )
            for row in rows
        )

    def delete_by_document_id(
        self,
        document_id: UUID,
    ) -> None:
        """Delete all chunks belonging to a document."""
        with self._get_connection() as conn:
            conn.execute(
                text("""
                DELETE FROM document_chunks
                WHERE document_id = :document_id
                """),
                {"document_id": str(document_id)},
            )
            conn.commit()

    def count_by_document_id(
        self,
        document_id: UUID,
    ) -> int:
        """Return the number of chunks stored for a document."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                text("""
                SELECT COUNT(*)
                FROM document_chunks
                WHERE document_id = :document_id
                """),
                {"document_id": str(document_id)},
            )
            return int(cursor.fetchone()[0])
