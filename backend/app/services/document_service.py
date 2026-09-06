import os
import uuid
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import HTTPException, UploadFile

from app.models.document import Document, DocumentRole
from app.repositories.document_repository import DocumentRepository
from app.storage.local_storage import LocalStorage

# ---------------------------------------------------------------------------
# Allowed types registry - extend here, nowhere else
# ---------------------------------------------------------------------------

ALLOWED_TYPES: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
}

ALLOWED_EXTENSIONS: set[str] = set(ALLOWED_TYPES.values())


class DocumentService:
    """
    Owns the document ingestion workflow.
    Routes call this service; they do not contain business logic.
    """

    def __init__(
        self,
        repository: DocumentRepository,
        storage: LocalStorage,
        max_upload_bytes: int,
    ) -> None:
        self._repo = repository
        self._storage = storage
        self._max_bytes = max_upload_bytes

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    async def upload_document(
        self,
        file: UploadFile,
        role: DocumentRole = DocumentRole.OTHER,
    ) -> Document:
        self._validate(file)

        content_type = file.content_type or ""
        _, ext = os.path.splitext(file.filename or "")
        ext = ext.lower()

        document_id = uuid.uuid4()

        # --- persist file first ---
        try:
            stored_name, storage_path = await self._storage.save_file(
                file, document_id
            )
            if not self._storage.file_exists(storage_path):
                raise RuntimeError("Stored file could not be verified")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except Exception:
            raise HTTPException(status_code=500, detail="File storage failed")

        # --- persist metadata; rollback file on failure ---
        now = datetime.now(timezone.utc)
        doc = Document(
            id=document_id,
            original_filename=file.filename or "unknown",
            stored_filename=stored_name,
            content_type=content_type,
            extension=ext,
            size_bytes=file.size or 0,
            status="uploaded",
            storage_path=storage_path,
            created_at=now,
            updated_at=now,
            role=role,
        )
        try:
            self._repo.create(doc)
        except Exception:
            self._storage.delete_document_dir(document_id)
            raise HTTPException(
                status_code=500,
                detail="Metadata persistence failed",
            )

        return doc

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def list_documents(self) -> List[Document]:
        return self._repo.list_documents()

    def get_document(self, document_id: UUID) -> Document:
        doc = self._repo.get_by_id(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc

    def delete_document(self, document_id: UUID) -> None:
        doc = self._repo.get_by_id(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        self._storage.delete_document_dir(document_id)
        self._repo.delete(document_id)

    # ------------------------------------------------------------------
    # Private: validation
    # ------------------------------------------------------------------

    def _validate(self, file: UploadFile) -> None:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file extension '{ext}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        content_type = file.content_type or ""
        if content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported media type '{content_type}'",
            )

        # Cross-check extension vs declared content-type
        if ALLOWED_TYPES[content_type] != ext:
            raise HTTPException(
                status_code=400,
                detail="File extension does not match declared content type",
            )

        size = file.size or 0
        if size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        if size > self._max_bytes:
            mb = self._max_bytes // (1024 * 1024)
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds the {mb} MB upload limit",
            )
