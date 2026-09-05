"""API schemas for inspection approval workflows."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.models.approval_workflow import ApprovalDecision


class ApprovalWorkflowRequest(BaseModel):
    """Request body for executing an approval workflow."""

    instruction: str = Field(min_length=1)
    document_ids: tuple[UUID, ...] = ()


class ApprovalWorkflowResponse(BaseModel):
    """Response returned after an approval workflow completes."""

    workflow_id: UUID
    decision: ApprovalDecision
    summary: str
    supporting_evidence: tuple[str, ...] = ()
    output_path: str | None = None
