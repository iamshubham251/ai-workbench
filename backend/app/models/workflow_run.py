from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class WorkflowRun:
    id: UUID
    document_id: Optional[UUID]
    user_id: UUID
    status: str
    decision: Optional[str]
    error_message: Optional[str]
    output_path: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
