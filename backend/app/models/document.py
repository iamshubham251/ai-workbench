from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Document:
    """
    Domain entity representing an ingested document.
    Status lifecycle: uploaded → processing → processed | failed
    """
    id: UUID
    original_filename: str
    stored_filename: str
    content_type: str
    extension: str
    size_bytes: int
    status: str
    storage_path: str
    created_at: datetime
    updated_at: datetime
