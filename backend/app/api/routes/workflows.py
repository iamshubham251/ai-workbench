from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.config.settings import settings
from app.dependencies import get_approval_workflow_service, get_current_user
from app.models.user import User
from app.models.workflow_run import WorkflowRun
from app.repositories.workflow_run_repository import WorkflowRunRepository
from app.schemas.approval_workflow import (
    ApprovalWorkflowRequest,
    ApprovalWorkflowResponse,
)
from app.schemas.workflow_run import WorkflowRunHistoryItem
from app.services.approval_workflow_service import ApprovalWorkflowService

router = APIRouter()

def get_workflow_run_repo():
    return WorkflowRunRepository()


@router.post("/approval", response_model=ApprovalWorkflowResponse)
def execute_approval_workflow(
    request: ApprovalWorkflowRequest,
    workflow_service: ApprovalWorkflowService = Depends(get_approval_workflow_service),
    current_user: User = Depends(get_current_user),
    run_repo: WorkflowRunRepository = Depends(get_workflow_run_repo)
):
    from datetime import datetime

    workflow_id = uuid4()
    output_path = Path(settings.OUTPUT_DIR) / f"approval_note_{workflow_id}.docx"

    document_id = request.document_ids[0] if request.document_ids else None

    run = WorkflowRun(
        id=workflow_id,
        document_id=document_id,
        user_id=current_user.id,
        status="RUNNING",
        decision=None,
        error_message=None,
        output_path=None,
        created_at=datetime.utcnow(),
        completed_at=None
    )
    run_repo.create(run)

    try:
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

        run.status = "COMPLETED"
        run.decision = result.decision
        run.output_path = str(output_path) if output_path.exists() else None
        run.completed_at = datetime.utcnow()
        run_repo.update(run)

        return ApprovalWorkflowResponse(
            workflow_id=result.workflow_id,
            decision=result.decision,
            summary=result.summary,
            supporting_evidence=result.supporting_evidence,
            findings=tuple(
                {"finding": f.finding, "severity": f.severity, "page_number": f.page_number}
                for f in result.findings
            ),
            output_path=run.output_path,
        )
    except Exception as e:
        run.status = "FAILED"
        run.error_message = str(e)
        run.completed_at = datetime.utcnow()
        run_repo.update(run)
        raise HTTPException(status_code=500, detail=str(e))


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
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        filename=requested_path.name,
    )


@router.get("/history", response_model=list[WorkflowRunHistoryItem])
def get_workflow_history(
    current_user: User = Depends(get_current_user),
    run_repo: WorkflowRunRepository = Depends(get_workflow_run_repo)
):
    from datetime import datetime
    items = run_repo.list_by_user_with_document_name(current_user.id)
    result = []
    for row in items:
        result.append(
            WorkflowRunHistoryItem(
                id=row["id"],
                document_id=row["document_id"],
                document_name=row["document_name"] or "Unknown Document",
                status=row["status"],
                decision=row["decision"],
                has_output=bool(row["output_path"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
            )
        )
    return result
