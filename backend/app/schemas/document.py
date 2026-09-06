from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentRole


class DocumentResponse(BaseModel):
    """
    Public response schema for a document.
    Intentionally omits internal fields: stored_filename, storage_path.
    """

    id: UUID
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int
    status: str
    role: DocumentRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
