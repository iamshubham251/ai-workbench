from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class WorkflowRunHistoryItem(BaseModel):
    id: UUID
    document_id: UUID
    document_name: str
    status: str
    decision: Optional[str] = None
    has_output: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
