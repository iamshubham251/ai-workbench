"""Orchestrate inspection analysis, approval decisions, and deliverables."""

from pathlib import Path
from uuid import UUID

from app.models.approval_workflow import ApprovalWorkflowResult
from app.services.approval_decision_service import ApprovalDecisionService
from app.services.approval_note_generator import ApprovalNoteGenerator
from app.services.document_content_service import DocumentContentService
from app.services.gemini_inspection_analyzer import GeminiInspectionAnalyzer
from app.services.rag_service import RagService


class ApprovalWorkflowService:
    """Run the complete inspection approval workflow."""

    def __init__(
        self,
        inspection_analyzer: GeminiInspectionAnalyzer,
        decision_service: ApprovalDecisionService | None = None,
        note_generator: ApprovalNoteGenerator | None = None,
        document_content_service: DocumentContentService | None = None,
        rag_service: RagService | None = None,
    ) -> None:
        self._inspection_analyzer = inspection_analyzer
        self._decision_service = decision_service or ApprovalDecisionService()
        self._note_generator = note_generator or ApprovalNoteGenerator()
        self._document_content_service = document_content_service
        self._rag_service = rag_service

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

    def execute_from_document(
        self,
        workflow_id: UUID,
        document_id: UUID,
        supporting_evidence: tuple[str, ...] = (),
        output_path: Path | None = None,
    ) -> ApprovalWorkflowResult:
        """Run the approval workflow using a stored inspection document."""
        if self._document_content_service is None:
            raise RuntimeError("document_content_service is not configured")

        content = self._document_content_service.get_content(document_id)

        if not content.full_text.strip():
            raise ValueError("Inspection document contains no readable text")

        evidence = supporting_evidence

        if self._rag_service is not None:
            rag_response = self._rag_service.query_all(
                content.full_text,
                top_k=5,
            )
            evidence = tuple(
                result.text
                for result in rag_response.results
                if result.text.strip()
            )

        return self.execute(
            workflow_id=workflow_id,
            inspection_text=content.full_text,
            supporting_evidence=evidence,
            output_path=output_path,
        )
