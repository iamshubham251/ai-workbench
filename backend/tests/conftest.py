"""
Pytest configuration and shared fixtures.

All tests use isolated temp directories for uploads and DB,
so they never touch production data and are fully repeatable.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.dependencies import get_document_service, get_current_user
from app.main import create_app
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.storage.local_storage import LocalStorage


@pytest.fixture(autouse=True)
def tmp_env(tmp_path: Path, monkeypatch):
    """
    Patch settings so each test gets its own upload dir and SQLite DB.
    """
    db_file = str(tmp_path / "test.db")
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    monkeypatch.setattr(settings, "DATABASE_URL", "")
    monkeypatch.setattr(settings, "DATABASE_PATH", db_file)
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(upload_dir))
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)

    from app.database import reset_engine
    reset_engine()

    return {"db": db_file, "uploads": upload_dir}


@pytest.fixture()
def client(tmp_env):
    """TestClient wired to isolated storage & DB via dependency override."""

    def _override_service():
        repo = DocumentRepository(db_path=tmp_env["db"])
        storage = LocalStorage(upload_dir=tmp_env["uploads"])
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        return DocumentService(
            repository=repo, storage=storage, max_upload_bytes=max_bytes
        )

    from app.main import app
    app.dependency_overrides[get_document_service] = _override_service
    
    # Create a real test user and valid token to bypass auth legitimately
    from app.models.user import User
    from app.repositories.user_repository import UserRepository
    from app.services.auth_service import AuthService
    from app.database import get_connection
    from uuid import uuid4
    
    test_user = User(id=uuid4(), email="test@example.com", hashed_password="pwd")
    
    with get_connection() as conn:
        user_repo = UserRepository()
        # Prevent UniqueViolation if the user already exists in shared DB
        try:
            test_user = user_repo.create(email=test_user.email, hashed_password=test_user.hashed_password)
        except Exception as e:
            print(f"Exception during user creation: {e}")
            test_user = user_repo.get_by_email(test_user.email)
            
        auth_service = AuthService(user_repo)
        token = auth_service.create_access_token({"sub": test_user.email})

    with TestClient(app) as c:
        c.headers.update({"Authorization": f"Bearer {token}"})
        yield c


# ---------------------------------------------------------------------------
# Helpers for building in-memory test files
# ---------------------------------------------------------------------------


def make_file(content: bytes, filename: str, content_type: str):
    """Return a tuple suitable for httpx multipart upload."""
    return ("file", (filename, content, content_type))


PDF_BYTES = b"%PDF-1.4 fake pdf content for testing"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DOCX_BYTES = b"PK\x03\x04fake docx"
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
