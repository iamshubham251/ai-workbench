"""Deterministic approval decision logic for inspection workflows."""

from app.models.approval_workflow import (
    ApprovalDecision,
    ApprovalWorkflowResult,
    InspectionFinding,
)


class ApprovalDecisionService:
    """Evaluate inspection findings using explicit, explainable rules."""

    HIGH_SEVERITY = "high"
    MEDIUM_SEVERITY = "medium"

    def evaluate(
        self,
        workflow_id,
        findings: tuple[InspectionFinding, ...],
        supporting_evidence: tuple[str, ...] = (),
    ) -> ApprovalWorkflowResult:
        if not findings:
            return ApprovalWorkflowResult(
                workflow_id=workflow_id,
                decision=ApprovalDecision.REVIEW,
                summary="No inspection findings were provided; manual review is required.",
                supporting_evidence=supporting_evidence,
            )

        normalized_severities = {
            finding.severity.strip().lower()
            for finding in findings
            if finding.severity.strip()
        }

        if self.HIGH_SEVERITY in normalized_severities:
            return ApprovalWorkflowResult(
                workflow_id=workflow_id,
                decision=ApprovalDecision.REJECT,
                summary="The inspection contains a high-severity finding and cannot be automatically approved.",
                supporting_evidence=supporting_evidence,
            )

        if self.MEDIUM_SEVERITY in normalized_severities:
            return ApprovalWorkflowResult(
                workflow_id=workflow_id,
                decision=ApprovalDecision.REVIEW,
                summary="The inspection contains a medium-severity finding and requires manual review.",
                supporting_evidence=supporting_evidence,
            )

        return ApprovalWorkflowResult(
            workflow_id=workflow_id,
            decision=ApprovalDecision.APPROVE,
            summary="No high- or medium-severity findings were identified; the inspection can be approved.",
            supporting_evidence=supporting_evidence,
        )
