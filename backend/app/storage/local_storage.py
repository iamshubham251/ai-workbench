import re
import shutil
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile


class LocalStorage:
    """
    Responsible for all filesystem operations.
    The service layer never constructs paths or writes files directly.
    """

    CHUNK_SIZE = 1024 * 1024  # 1 MB

    def __init__(self, upload_dir: Path) -> None:
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def save_file(self, file: UploadFile, document_id: UUID) -> tuple[str, str]:
        """
        Save *file* into upload_dir/<document_id>/<sanitized_filename>.

        Returns (stored_filename, storage_path).
        Raises ValueError for path-traversal attempts.
        """
        assert file.filename, "Filename must not be empty"

        sanitized = self._sanitize_filename(file.filename)
        doc_dir = self.upload_dir / str(document_id)
        doc_dir.mkdir(parents=True, exist_ok=True)
        file_path = doc_dir / sanitized

        # Guard: ensure resolved path stays inside upload_dir
        resolved = file_path.resolve()
        if not str(resolved).startswith(str(self.upload_dir.resolve())):
            raise ValueError("Path traversal attempt detected")

        await file.seek(0)
        with open(file_path, "wb") as buf:
            while chunk := await file.read(self.CHUNK_SIZE):
                buf.write(chunk)

        return sanitized, str(file_path)

    def delete_document_dir(self, document_id: UUID) -> None:
        """Remove the directory for a document (rollback / cleanup)."""
        doc_dir = self.upload_dir / str(document_id)
        if doc_dir.exists():
            shutil.rmtree(doc_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Strip directory components, then replace any character that is not
        alphanumeric, a dot, hyphen, or underscore with an underscore.
        Never trusts the original filename as a filesystem path.
        """
        # Strip any directory component (handles both / and \)
        basename = Path(filename).name
        # Collapse unsafe characters
        safe = re.sub(r"[^a-zA-Z0-9.\-_]", "_", basename)
        return safe or "unnamed_file"
