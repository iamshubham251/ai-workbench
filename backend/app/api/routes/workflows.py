from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.dependencies import get_approval_workflow_service
from app.config.settings import settings
from app.schemas.approval_workflow import (
    ApprovalWorkflowRequest,
    ApprovalWorkflowResponse,
)
from app.services.approval_workflow_service import ApprovalWorkflowService


router = APIRouter()


@router.post("/approval", response_model=ApprovalWorkflowResponse)
def execute_approval_workflow(
    request: ApprovalWorkflowRequest,
    workflow_service: ApprovalWorkflowService = Depends(
        get_approval_workflow_service
    ),
):
    workflow_id = uuid4()
    output_path = Path(settings.OUTPUT_DIR) / f"approval_note_{workflow_id}.docx"

    if request.document_ids:
        result = workflow_service.execute_from_document(
            workflow_id=workflow_id,
            document_id=request.document_ids[0],
            output_path=output_path,
        )
    else:
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
        output_path=str(output_path) if output_path.exists() else None,
    )


@router.get("/approval/output/{filename}")
def download_approval_note(filename: str):
    output_dir = Path(settings.OUTPUT_DIR).resolve()
    requested_path = (output_dir / filename).resolve()

    if requested_path.parent != output_dir:
        raise HTTPException(
            status_code=400,
            detail="Invalid output filename",
        )

    if requested_path.suffix.lower() != ".docx":
        raise HTTPException(
            status_code=400,
            detail="Only DOCX files are available",
        )

    if not requested_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Approval note not found",
        )

    return FileResponse(
        path=requested_path,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        filename=requested_path.name,
    )

