import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.database import get_connection
from app.models.document import Document, DocumentRole


class DocumentRepository:
    """
    All database access lives here. Uses SQLAlchemy to support both SQLite and PostgreSQL.
    """

    DDL = """
        CREATE TABLE IF NOT EXISTS documents (
            id                VARCHAR(36) PRIMARY KEY,
            original_filename VARCHAR(255) NOT NULL,
            stored_filename   VARCHAR(255) NOT NULL,
            content_type      VARCHAR(100) NOT NULL,
            extension         VARCHAR(10) NOT NULL,
            size_bytes        INTEGER NOT NULL,
            status            VARCHAR(50) NOT NULL,
            storage_path      VARCHAR(500) NOT NULL,
            created_at        VARCHAR(50) NOT NULL,
            updated_at        VARCHAR(50) NOT NULL,
            role              VARCHAR(50) NOT NULL DEFAULT 'other'
        )
    """

    def __init__(self, db_path: str = "") -> None:
        # db_path is kept for backwards compatibility in dependencies.py
        self._init_schema()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(text(self.DDL))
            
            # Note: For strict Postgres compatibility, ALTER TABLE IF NOT EXISTS 
            # is better, or using Alembic for migrations. For now, we skip the 
            # SQLite-specific pragma check if we are in Postgres.
            if conn.engine.dialect.name == "sqlite":
                columns = {
                    row._mapping["name"]
                    for row in conn.execute(text("PRAGMA table_info(documents)")).fetchall()
                }
                if "role" not in columns:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'other'"))
            conn.commit()

    def create(self, doc: Document) -> Document:
        with self._connect() as conn:
            conn.execute(
                text("""
                INSERT INTO documents (
                    id, original_filename, stored_filename, content_type,
                    extension, size_bytes, status, storage_path,
                    created_at, updated_at, role
                ) VALUES (
                    :id, :original_filename, :stored_filename, :content_type,
                    :extension, :size_bytes, :status, :storage_path,
                    :created_at, :updated_at, :role
                )
                """),
                {
                    "id": str(doc.id),
                    "original_filename": doc.original_filename,
                    "stored_filename": doc.stored_filename,
                    "content_type": doc.content_type,
                    "extension": doc.extension,
                    "size_bytes": doc.size_bytes,
                    "status": doc.status,
                    "storage_path": doc.storage_path,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat(),
                    "role": doc.role.value,
                },
            )
            conn.commit()
        return doc

    def list_documents(self) -> List[Document]:
        with self._connect() as conn:
            # Postgres doesn't have rowid, fallback to created_at
            rows = conn.execute(
                text("SELECT * FROM documents ORDER BY created_at DESC")
            ).fetchall()
        return [self._row_to_doc(r) for r in rows]

    def get_by_id(self, document_id: UUID) -> Optional[Document]:
        with self._connect() as conn:
            row = conn.execute(
                text("SELECT * FROM documents WHERE id = :id"), 
                {"id": str(document_id)}
            ).fetchone()
        return self._row_to_doc(row) if row else None

    def list_documents_by_role(self, role: DocumentRole) -> List[Document]:
        with self._connect() as conn:
            rows = conn.execute(
                text("SELECT * FROM documents WHERE role = :role ORDER BY created_at DESC"),
                {"role": role.value},
            ).fetchall()
        return [self._row_to_doc(row) for row in rows]

    def delete(self, document_id: UUID) -> bool:
        with self._connect() as conn:
            result = conn.execute(
                text("DELETE FROM documents WHERE id = :id"), 
                {"id": str(document_id)}
            )
            conn.commit()
        return result.rowcount > 0

    def _connect(self) -> Connection:
        return get_connection()

    @staticmethod
    def _row_to_doc(row) -> Document:
        mapping = row._mapping
        role = mapping.get("role", DocumentRole.OTHER.value)

        try:
            document_role = DocumentRole(role)
        except ValueError:
            document_role = DocumentRole.OTHER

        return Document(
            id=UUID(mapping["id"]),
            original_filename=mapping["original_filename"],
            stored_filename=mapping["stored_filename"],
            content_type=mapping["content_type"],
            extension=mapping["extension"],
            size_bytes=mapping["size_bytes"],
            status=mapping["status"],
            storage_path=mapping["storage_path"],
            created_at=datetime.fromisoformat(mapping["created_at"]),
            updated_at=datetime.fromisoformat(mapping["updated_at"]),
            role=document_role,
        )
