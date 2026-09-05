from pathlib import Path
from uuid import uuid4

from docx import Document

from app.models.approval_workflow import (
    ApprovalDecision,
    ApprovalWorkflowResult,
)
from app.services.approval_note_generator import ApprovalNoteGenerator


def make_result() -> ApprovalWorkflowResult:
    return ApprovalWorkflowResult(
        workflow_id=uuid4(),
        decision=ApprovalDecision.APPROVE,
        summary="No high- or medium-severity findings were identified.",
        supporting_evidence=(
            "SOP section 4.2 requires the inspected component to remain within tolerance.",
            "Inspection report page 3 confirms the measured value is within tolerance.",
        ),
    )


def test_generates_docx(tmp_path: Path) -> None:
    output_path = tmp_path / "approval_note.docx"

    result = ApprovalNoteGenerator().generate(
        make_result(),
        output_path,
    )

    assert result == output_path
    assert output_path.exists()


def test_generated_docx_contains_expected_content(tmp_path: Path) -> None:
    output_path = tmp_path / "approval_note.docx"

    workflow_result = make_result()

    ApprovalNoteGenerator().generate(
        workflow_result,
        output_path,
    )

    document = Document(output_path)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert "Inspection Approval Note" in text
    assert str(workflow_result.workflow_id) in text
    assert "APPROVE" in text
    assert workflow_result.summary in text
    assert workflow_result.supporting_evidence[0] in text
    assert workflow_result.supporting_evidence[1] in text


def test_generates_output_directory(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "outputs" / "approval_note.docx"

    ApprovalNoteGenerator().generate(
        make_result(),
        output_path,
    )

    assert output_path.exists()
