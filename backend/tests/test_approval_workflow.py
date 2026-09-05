from uuid import uuid4

import pytest

from app.models.approval_workflow import (
    ApprovalDecision,
    ApprovalWorkflowRequest,
    ApprovalWorkflowResult,
    InspectionFinding,
)


def test_inspection_finding_accepts_valid_data():
    finding = InspectionFinding(
        finding="Emergency stop was not functional.",
        severity="high",
        page_number=3,
    )

    assert finding.finding == "Emergency stop was not functional."
    assert finding.severity == "high"
    assert finding.page_number == 3


def test_inspection_finding_rejects_empty_finding():
    with pytest.raises(ValueError, match="finding must not be empty"):
        InspectionFinding(finding=" ")


def test_inspection_finding_rejects_invalid_page():
    with pytest.raises(ValueError, match="page_number must be one-based"):
        InspectionFinding(finding="Missing guard", page_number=0)


def test_workflow_request_accepts_valid_data():
    document_id = uuid4()

    request = ApprovalWorkflowRequest(
        workflow_id=uuid4(),
        instruction="Determine whether this inspection can be approved.",
        document_ids=(document_id,),
    )

    assert request.instruction.startswith("Determine")
    assert request.document_ids == (document_id,)


def test_workflow_request_rejects_empty_instruction():
    with pytest.raises(ValueError, match="instruction must not be empty"):
        ApprovalWorkflowRequest(
            workflow_id=uuid4(),
            instruction=" ",
        )


def test_workflow_result_accepts_valid_data():
    result = ApprovalWorkflowResult(
        workflow_id=uuid4(),
        decision=ApprovalDecision.APPROVE,
        summary="Inspection satisfies the applicable SOP requirements.",
        supporting_evidence=("SOP section 4.2",),
    )

    assert result.decision is ApprovalDecision.APPROVE
    assert result.supporting_evidence == ("SOP section 4.2",)


def test_workflow_result_rejects_empty_summary():
    with pytest.raises(ValueError, match="summary must not be empty"):
        ApprovalWorkflowResult(
            workflow_id=uuid4(),
            decision=ApprovalDecision.REVIEW,
            summary=" ",
        )
