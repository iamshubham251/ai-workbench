"""
Dependency injection for the application.
Each request gets a fresh DocumentService wired to the configured
repository and storage instances.
"""

from pathlib import Path

from app.config.settings import settings
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.storage.local_storage import LocalStorage


def get_document_service() -> DocumentService:
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    repository = DocumentRepository(db_path=db_path)
    storage = LocalStorage(upload_dir=Path(settings.UPLOAD_DIR))
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    return DocumentService(
        repository=repository,
        storage=storage,
        max_upload_bytes=max_bytes,
    )
