from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
