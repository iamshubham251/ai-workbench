from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class DocumentRole(str, Enum):
    INSPECTION_REPORT = "inspection_report"
    SOP = "sop"
    OTHER = "other"


@dataclass
class Document:
    """
    Domain entity representing an ingested document.
    Status lifecycle: uploaded -> processing -> processed | failed
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
    role: DocumentRole = DocumentRole.OTHER
