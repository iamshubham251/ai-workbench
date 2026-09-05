from uuid import uuid4

from app.models.approval_workflow import ApprovalDecision, InspectionFinding
from app.services.approval_decision_service import ApprovalDecisionService


def test_high_severity_finding_rejects():
    service = ApprovalDecisionService()

    result = service.evaluate(
        workflow_id=uuid4(),
        findings=(
            InspectionFinding(
                finding="Emergency stop is not functional.",
                severity="high",
            ),
        ),
    )

    assert result.decision is ApprovalDecision.REJECT


def test_medium_severity_finding_requires_review():
    service = ApprovalDecisionService()

    result = service.evaluate(
        workflow_id=uuid4(),
        findings=(
            InspectionFinding(
                finding="Guarding requires maintenance.",
                severity="medium",
            ),
        ),
    )

    assert result.decision is ApprovalDecision.REVIEW


def test_low_severity_findings_can_be_approved():
    service = ApprovalDecisionService()

    result = service.evaluate(
        workflow_id=uuid4(),
        findings=(
            InspectionFinding(
                finding="Minor surface wear observed.",
                severity="low",
            ),
        ),
    )

    assert result.decision is ApprovalDecision.APPROVE


def test_no_findings_requires_review():
    service = ApprovalDecisionService()

    result = service.evaluate(
        workflow_id=uuid4(),
        findings=(),
    )

    assert result.decision is ApprovalDecision.REVIEW


def test_high_severity_takes_priority_over_medium():
    service = ApprovalDecisionService()

    result = service.evaluate(
        workflow_id=uuid4(),
        findings=(
            InspectionFinding(finding="Minor issue", severity="medium"),
            InspectionFinding(finding="Critical issue", severity="high"),
        ),
    )

    assert result.decision is ApprovalDecision.REJECT


def test_supporting_evidence_is_preserved():
    evidence = ("SOP section 4.2", "Inspection report page 3")

    result = ApprovalDecisionService().evaluate(
        workflow_id=uuid4(),
        findings=(
            InspectionFinding(finding="Minor wear", severity="low"),
        ),
        supporting_evidence=evidence,
    )

    assert result.supporting_evidence == evidence
