from unittest.mock import Mock
from uuid import uuid4

from app.models.approval_workflow import ApprovalDecision, ApprovalWorkflowResult
from app.models.document_content import DocumentContent
from app.services.approval_workflow_service import ApprovalWorkflowService
from app.services.rag_service import RagResponse
from app.services.retriever import RetrievalResult


def test_execute_from_document_retrieves_sop_evidence():
    workflow_id = uuid4()
    document_id = uuid4()

    document_content_service = Mock()
    document_content_service.get_content.return_value = DocumentContent(
        document_id=document_id,
        pages=("Inspection finding: conveyor belt joint damaged.",),
    )

    rag_service = Mock()
    rag_service.query_all.return_value = RagResponse(
        query="Inspection finding: conveyor belt joint damaged.",
        answer="The SOP requires immediate inspection of damaged belt joints.",
        results=(
            RetrievalResult(
                document_id=uuid4(),
                chunk_index=2,
                text="Damaged belt joints must be isolated and inspected.",
                score=0.91,
                page_numbers=(4,),
                section_title="Belt Joint Inspection",
            ),
        ),
    )

    workflow = ApprovalWorkflowService(
        inspection_analyzer=Mock(),
        document_content_service=document_content_service,
        rag_service=rag_service,
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

    rag_service.query_all.assert_called_once_with(
        "Inspection finding: conveyor belt joint damaged.",
        top_k=5,
    )

    workflow.execute.assert_called_once_with(
        workflow_id=workflow_id,
        inspection_text="Inspection finding: conveyor belt joint damaged.",
        supporting_evidence=(
            "Damaged belt joints must be isolated and inspected.",
        ),
        output_path=None,
    )


def test_execute_from_document_continues_without_sop_evidence():
    workflow_id = uuid4()
    document_id = uuid4()

    document_content_service = Mock()
    document_content_service.get_content.return_value = DocumentContent(
        document_id=document_id,
        pages=("Inspection finding: minor surface wear.",),
    )

    rag_service = Mock()
    rag_service.query_all.return_value = RagResponse(
        query="Inspection finding: minor surface wear.",
        answer="No supporting evidence was found for this query.",
        results=(),
    )

    workflow = ApprovalWorkflowService(
        inspection_analyzer=Mock(),
        document_content_service=document_content_service,
        rag_service=rag_service,
    )

    expected = ApprovalWorkflowResult(
        workflow_id=workflow_id,
        decision=ApprovalDecision.APPROVE,
        summary="No high- or medium-severity findings.",
    )

    workflow.execute = Mock(return_value=expected)

    result = workflow.execute_from_document(
        workflow_id=workflow_id,
        document_id=document_id,
    )

    assert result is expected
    workflow.execute.assert_called_once_with(
        workflow_id=workflow_id,
        inspection_text="Inspection finding: minor surface wear.",
        supporting_evidence=(),
        output_path=None,
    )
