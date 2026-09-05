"""SQLite repository for persistent document chunks."""

import sqlite3
from uuid import UUID

from app.models.document_chunk import DocumentChunk


class SqlChunkRepository:
    """Persist and retrieve document chunks using SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self._create_table()

    def _create_table(self) -> None:
        """Create the document chunks table if it does not exist."""
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS document_chunks (
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                page_numbers TEXT NOT NULL,
                section_title TEXT,
                PRIMARY KEY (document_id, chunk_index)
            )
            """
        )
        self.connection.commit()

    def save(
        self,
        document_id: UUID,
        chunks: tuple[DocumentChunk, ...],
    ) -> None:
        """Replace all stored chunks for a document."""
        self.delete_by_document_id(document_id)

        self.connection.executemany(
            """
            INSERT INTO document_chunks (
                document_id,
                chunk_index,
                text,
                page_numbers,
                section_title
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    str(document_id),
                    chunk.chunk_index,
                    chunk.text,
                    ",".join(
                        str(page)
                        for page in chunk.page_numbers
                    ),
                    chunk.section_title,
                )
                for chunk in chunks
            ],
        )

        self.connection.commit()

    def get_by_document_id(
        self,
        document_id: UUID,
    ) -> tuple[DocumentChunk, ...]:
        """Return all chunks for a document in chunk order."""
        cursor = self.connection.execute(
            """
            SELECT
                chunk_index,
                text,
                page_numbers,
                section_title
            FROM document_chunks
            WHERE document_id = ?
            ORDER BY chunk_index ASC
            """,
            (str(document_id),),
        )

        rows = cursor.fetchall()

        return tuple(
            DocumentChunk(
                document_id=document_id,
                chunk_index=row[0],
                text=row[1],
                page_numbers=tuple(
                    int(page)
                    for page in row[2].split(",")
                    if page
                ),
                section_title=row[3],
            )
            for row in rows
        )

    def get_all(self) -> tuple[DocumentChunk, ...]:
        """Return all stored chunks in stable document and chunk order."""
        cursor = self.connection.execute(
            """
            SELECT
                document_id,
                chunk_index,
                text,
                page_numbers,
                section_title
            FROM document_chunks
            ORDER BY document_id ASC, chunk_index ASC
            """
        )

        rows = cursor.fetchall()

        return tuple(
            DocumentChunk(
                document_id=UUID(row[0]),
                chunk_index=row[1],
                text=row[2],
                page_numbers=tuple(
                    int(page)
                    for page in row[3].split(",")
                    if page
                ),
                section_title=row[4],
            )
            for row in rows
        )
    def delete_by_document_id(
        self,
        document_id: UUID,
    ) -> None:
        """Delete all chunks belonging to a document."""
        self.connection.execute(
            """
            DELETE FROM document_chunks
            WHERE document_id = ?
            """,
            (str(document_id),),
        )
        self.connection.commit()

    def count_by_document_id(
        self,
        document_id: UUID,
    ) -> int:
        """Return the number of chunks stored for a document."""
        cursor = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM document_chunks
            WHERE document_id = ?
            """,
            (str(document_id),),
        )

        return int(cursor.fetchone()[0])

