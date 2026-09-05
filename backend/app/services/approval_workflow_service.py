"""Orchestrate inspection analysis, approval decisions, and deliverables."""

from pathlib import Path
from uuid import UUID

from app.models.approval_workflow import ApprovalWorkflowResult
from app.services.approval_decision_service import ApprovalDecisionService
from app.services.approval_note_generator import ApprovalNoteGenerator
from app.services.gemini_inspection_analyzer import GeminiInspectionAnalyzer


class ApprovalWorkflowService:
    """Run the complete inspection approval workflow."""

    def __init__(
        self,
        inspection_analyzer: GeminiInspectionAnalyzer,
        decision_service: ApprovalDecisionService | None = None,
        note_generator: ApprovalNoteGenerator | None = None,
    ) -> None:
        self._inspection_analyzer = inspection_analyzer
        self._decision_service = decision_service or ApprovalDecisionService()
        self._note_generator = note_generator or ApprovalNoteGenerator()

    def execute(
        self,
        workflow_id: UUID,
        inspection_text: str,
        supporting_evidence: tuple[str, ...] = (),
        output_path: Path | None = None,
    ) -> ApprovalWorkflowResult:
        if not inspection_text.strip():
            raise ValueError("inspection_text must not be empty")

        findings = self._inspection_analyzer.analyze(
            inspection_text=inspection_text,
            supporting_evidence=supporting_evidence,
        )

        result = self._decision_service.evaluate(
            workflow_id=workflow_id,
            findings=findings,
            supporting_evidence=supporting_evidence,
        )

        if output_path is not None:
            self._note_generator.generate(
                result=result,
                output_path=output_path,
            )

        return result
