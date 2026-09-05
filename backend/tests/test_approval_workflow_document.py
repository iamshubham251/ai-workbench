from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

from app.models.approval_workflow import ApprovalDecision, ApprovalWorkflowResult
from app.models.document_content import DocumentContent
from app.services.approval_workflow_service import ApprovalWorkflowService


def test_execute_from_document_uses_normalized_document_text():
    workflow_id = uuid4()
    document_id = uuid4()

    document_content_service = Mock()
    document_content_service.get_content.return_value = DocumentContent(
        document_id=document_id,
        pages=("Inspection finding: conveyor belt joint damaged.",),
    )

    workflow = ApprovalWorkflowService(
        inspection_analyzer=Mock(),
        document_content_service=document_content_service,
    )

    expected = ApprovalWorkflowResult(
        workflow_id=workflow_id,
        decision=ApprovalDecision.REVIEW,
        summary="Review required.",
    )

    workflow.execute = Mock(return_value=expected)

    result = workflow.execute_from_document(
        workflow_id=workflow_id,
        document_id=document_id,
    )

    assert result is expected
    document_content_service.get_content.assert_called_once_with(document_id)

    workflow.execute.assert_called_once_with(
        workflow_id=workflow_id,
        inspection_text="Inspection finding: conveyor belt joint damaged.",
        supporting_evidence=(),
        output_path=None,
    )


def test_execute_from_document_rejects_empty_document():
    document_id = uuid4()

    document_content_service = Mock()
    document_content_service.get_content.return_value = DocumentContent(
        document_id=document_id,
        pages=(),
    )

    workflow = ApprovalWorkflowService(
        inspection_analyzer=Mock(),
        document_content_service=document_content_service,
    )

    try:
        workflow.execute_from_document(
            workflow_id=uuid4(),
            document_id=document_id,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Inspection document contains no readable text"
