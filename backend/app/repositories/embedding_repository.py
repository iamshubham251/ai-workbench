"""SQLite repository for document embeddings."""

import sqlite3
from uuid import UUID

from app.models.embedding import DocumentEmbedding


class EmbeddingRepository:
    """Persist and retrieve document chunk embeddings using SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self._create_table()

    def _create_table(self) -> None:
        """Create the embeddings table if it does not exist."""
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS document_embeddings (
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                vector TEXT NOT NULL,
                dimensions INTEGER NOT NULL,
                PRIMARY KEY (document_id, chunk_index)
            )
            """
        )
        self.connection.commit()

    def save(
        self,
        document_id: UUID,
        embeddings: tuple[DocumentEmbedding, ...],
    ) -> None:
        """Replace all stored embeddings for a document."""
        self.delete_by_document_id(document_id)

        self.connection.executemany(
            """
            INSERT INTO document_embeddings (
                document_id,
                chunk_index,
                vector,
                dimensions
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    str(document_id),
                    embedding.chunk_index,
                    ",".join(
                        str(value)
                        for value in embedding.vector
                    ),
                    embedding.dimensions,
                )
                for embedding in embeddings
            ],
        )

        self.connection.commit()

    def get_by_document_id(
        self,
        document_id: UUID,
    ) -> tuple[DocumentEmbedding, ...]:
        """Return all embeddings for a document in chunk order."""
        cursor = self.connection.execute(
            """
            SELECT
                chunk_index,
                vector,
                dimensions
            FROM document_embeddings
            WHERE document_id = ?
            ORDER BY chunk_index ASC
            """,
            (str(document_id),),
        )

        rows = cursor.fetchall()

        return tuple(
            DocumentEmbedding(
                document_id=document_id,
                chunk_index=row[0],
                vector=tuple(
                    float(value)
                    for value in row[1].split(",")
                    if value
                ),
            )
            for row in rows
        )

    def get_all(self) -> tuple[DocumentEmbedding, ...]:
        """Return all stored embeddings in stable document and chunk order."""
        cursor = self.connection.execute(
            """
            SELECT
                document_id,
                chunk_index,
                vector,
                dimensions
            FROM document_embeddings
            ORDER BY document_id ASC, chunk_index ASC
            """
        )

        rows = cursor.fetchall()

        return tuple(
            DocumentEmbedding(
                document_id=UUID(row[0]),
                chunk_index=row[1],
                vector=tuple(
                    float(value)
                    for value in row[2].split(",")
                    if value
                ),
            )
            for row in rows
        )
    def delete_by_document_id(
        self,
        document_id: UUID,
    ) -> None:
        """Delete all embeddings belonging to a document."""
        self.connection.execute(
            """
            DELETE FROM document_embeddings
            WHERE document_id = ?
            """,
            (str(document_id),),
        )
        self.connection.commit()

    def count_by_document_id(
        self,
        document_id: UUID,
    ) -> int:
        """Return the number of embeddings stored for a document."""
        cursor = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM document_embeddings
            WHERE document_id = ?
            """,
            (str(document_id),),
        )

        return int(cursor.fetchone()[0])

