import sqlite3
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.models.document import Document


class DocumentRepository:
    """
    All SQLite access lives here. No SQL leaks into service or route layers.
    """

    DDL = """
        CREATE TABLE IF NOT EXISTS documents (
            id               TEXT PRIMARY KEY,
            original_filename TEXT NOT NULL,
            stored_filename  TEXT NOT NULL,
            content_type     TEXT NOT NULL,
            extension        TEXT NOT NULL,
            size_bytes       INTEGER NOT NULL,
            status           TEXT NOT NULL,
            storage_path     TEXT NOT NULL,
            created_at       TEXT NOT NULL,
            updated_at       TEXT NOT NULL
        )
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(self.DDL)

    # ------------------------------------------------------------------
    # Public operations
    # ------------------------------------------------------------------

    def create(self, doc: Document) -> Document:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    id, original_filename, stored_filename, content_type,
                    extension, size_bytes, status, storage_path,
                    created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    str(doc.id),
                    doc.original_filename,
                    doc.stored_filename,
                    doc.content_type,
                    doc.extension,
                    doc.size_bytes,
                    doc.status,
                    doc.storage_path,
                    doc.created_at.isoformat(),
                    doc.updated_at.isoformat(),
                ),
            )
        return doc

    def list_documents(self) -> List[Document]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM documents ORDER BY created_at DESC"
            ).fetchall()
        return [self._row_to_doc(r) for r in rows]

    def get_by_id(self, document_id: UUID) -> Optional[Document]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (str(document_id),)
            ).fetchone()
        return self._row_to_doc(row) if row else None

    def delete(self, document_id: UUID) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM documents WHERE id = ?", (str(document_id),)
            )
        return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_doc(row: sqlite3.Row) -> Document:
        return Document(
            id=UUID(row["id"]),
            original_filename=row["original_filename"],
            stored_filename=row["stored_filename"],
            content_type=row["content_type"],
            extension=row["extension"],
            size_bytes=row["size_bytes"],
            status=row["status"],
            storage_path=row["storage_path"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
