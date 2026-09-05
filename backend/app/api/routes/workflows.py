"""Inspection approval workflow routes."""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends

from app.config.settings import settings
from app.dependencies import get_approval_workflow_service
from app.schemas.approval_workflow import (
    ApprovalWorkflowRequest,
    ApprovalWorkflowResponse,
)
from app.services.approval_workflow_service import ApprovalWorkflowService


router = APIRouter()


@router.post(
    "/approval",
    response_model=ApprovalWorkflowResponse,
)
def execute_approval_workflow(
    request: ApprovalWorkflowRequest,
    workflow_service: ApprovalWorkflowService = Depends(
        get_approval_workflow_service
    ),
) -> ApprovalWorkflowResponse:
    """Execute an inspection approval workflow."""

    workflow_id = uuid4()
    output_path = (
        Path(settings.OUTPUT_DIR)
        / f"approval_note_{workflow_id}.docx"
    )

    result = workflow_service.execute(
        workflow_id=workflow_id,
        inspection_text=request.instruction,
        output_path=output_path,
    )

    return ApprovalWorkflowResponse(
        workflow_id=result.workflow_id,
        decision=result.decision,
        summary=result.summary,
        supporting_evidence=result.supporting_evidence,
        output_path=str(output_path),
    )
