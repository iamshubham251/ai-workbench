from pathlib import Path
from uuid import uuid4

from docx import Document

from app.models.approval_workflow import (
    ApprovalDecision,
    InspectionFinding,
)
from app.services.approval_decision_service import ApprovalDecisionService
from app.services.approval_workflow_service import ApprovalWorkflowService
from app.services.gemini_inspection_analyzer import GeminiInspectionAnalyzer


class FakeModelProvider:
    @property
    def name(self):
        return "fake-model"

    @property
    def capabilities(self):
        return ()

    def generate(self, request):
        from app.models.model import ModelResponse

        return ModelResponse(
            output="- finding: Emergency stop failed. | severity: high | page: 4",
            model_name=self.name,
        )


class FakeInspectionAnalyzer:
    def analyze(
        self,
        inspection_text: str,
        supporting_evidence: tuple[str, ...] = (),
    ) -> tuple[InspectionFinding, ...]:
        return (
            InspectionFinding(
                finding="Inspection passed without significant issues.",
                severity="low",
                page_number=1,
            ),
        )


def test_workflow_extracts_findings_and_rejects_high_severity():
    analyzer = GeminiInspectionAnalyzer(FakeModelProvider())
    service = ApprovalWorkflowService(
        inspection_analyzer=analyzer,
    )

    result = service.execute(
        workflow_id=uuid4(),
        inspection_text="Emergency stop was not functional.",
    )

    assert result.decision is ApprovalDecision.REJECT
    assert "high-severity" in result.summary


def test_workflow_passes_sop_evidence_to_result():
    evidence = ("SOP section 4.2 requires a functional emergency stop.",)

    result = ApprovalWorkflowService(
        inspection_analyzer=GeminiInspectionAnalyzer(FakeModelProvider()),
    ).execute(
        workflow_id=uuid4(),
        inspection_text="Emergency stop was not functional.",
        supporting_evidence=evidence,
    )

    assert result.supporting_evidence == evidence


def test_workflow_rejects_empty_inspection():
    service = ApprovalWorkflowService(
        inspection_analyzer=GeminiInspectionAnalyzer(FakeModelProvider()),
    )

    try:
        service.execute(
            workflow_id=uuid4(),
            inspection_text=" ",
        )
    except ValueError as exc:
        assert str(exc) == "inspection_text must not be empty"
    else:
        raise AssertionError("Expected ValueError")


def test_execute_generates_approval_note(tmp_path: Path) -> None:
    output_path = tmp_path / "approval_note.docx"

    result = ApprovalWorkflowService(
        inspection_analyzer=FakeInspectionAnalyzer(),
    ).execute(
        workflow_id=uuid4(),
        inspection_text="Inspection report content.",
        supporting_evidence=("SOP evidence",),
        output_path=output_path,
    )

    assert result.decision == ApprovalDecision.APPROVE
    assert output_path.exists()

    document = Document(output_path)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert "Inspection Approval Note" in text
    assert "APPROVE" in text
    assert "SOP evidence" in text
