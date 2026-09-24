"""SQLAlchemy repository for document embeddings."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.database import get_connection
from app.models.embedding import DocumentEmbedding


class EmbeddingRepository:
    """Persist and retrieve document chunk embeddings using SQLAlchemy."""

    def __init__(self, connection=None) -> None:
        self._create_table()

    def _get_connection(self) -> Connection:
        return get_connection()

    def _create_table(self) -> None:
        """Create the embeddings table if it does not exist."""
        with self._get_connection() as conn:
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    document_id VARCHAR(36) NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    vector TEXT NOT NULL,
                    dimensions INTEGER NOT NULL,
                    PRIMARY KEY (document_id, chunk_index)
                )
                """)
            )
            conn.commit()

    def save(
        self,
        document_id: UUID,
        embeddings: tuple[DocumentEmbedding, ...],
    ) -> None:
        """Replace all stored embeddings for a document."""
        self.delete_by_document_id(document_id)

        if not embeddings:
            return

        with self._get_connection() as conn:
            conn.execute(
                text("""
                INSERT INTO document_embeddings (
                    document_id,
                    chunk_index,
                    vector,
                    dimensions
                )
                VALUES (
                    :document_id, :chunk_index, :vector, :dimensions
                )
                """),
                [
                    {
                        "document_id": str(document_id),
                        "chunk_index": embedding.chunk_index,
                        "vector": ",".join(
                            str(value) for value in embedding.vector
                        ),
                        "dimensions": embedding.dimensions,
                    }
                    for embedding in embeddings
                ],
            )
            conn.commit()

    def get_by_document_id(
        self,
        document_id: UUID,
    ) -> tuple[DocumentEmbedding, ...]:
        """Return all embeddings for a document in chunk order."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                text("""
                SELECT
                    chunk_index,
                    vector,
                    dimensions
                FROM document_embeddings
                WHERE document_id = :document_id
                ORDER BY chunk_index ASC
                """),
                {"document_id": str(document_id)},
            )
            rows = cursor.fetchall()

        return tuple(
            DocumentEmbedding(
                document_id=document_id,
                chunk_index=row._mapping["chunk_index"],
                vector=tuple(
                    float(value)
                    for value in row._mapping["vector"].split(",")
                    if value
                ),
            )
            for row in rows
        )

    def get_all(self) -> tuple[DocumentEmbedding, ...]:
        """Return all stored embeddings in stable document and chunk order."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                text("""
                SELECT
                    document_id,
                    chunk_index,
                    vector,
                    dimensions
                FROM document_embeddings
                ORDER BY document_id ASC, chunk_index ASC
                """)
            )
            rows = cursor.fetchall()

        return tuple(
            DocumentEmbedding(
                document_id=UUID(row._mapping["document_id"]),
                chunk_index=row._mapping["chunk_index"],
                vector=tuple(
                    float(value)
                    for value in row._mapping["vector"].split(",")
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
        with self._get_connection() as conn:
            conn.execute(
                text("""
                DELETE FROM document_embeddings
                WHERE document_id = :document_id
                """),
                {"document_id": str(document_id)},
            )
            conn.commit()

    def count_by_document_id(
        self,
        document_id: UUID,
    ) -> int:
        """Return the number of embeddings stored for a document."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                text("""
                SELECT COUNT(*)
                FROM document_embeddings
                WHERE document_id = :document_id
                """),
                {"document_id": str(document_id)},
            )
            return int(cursor.fetchone()[0])
