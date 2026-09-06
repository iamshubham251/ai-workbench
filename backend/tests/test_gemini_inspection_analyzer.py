from uuid import uuid4

from app.ai.deterministic_provider import DeterministicModelProvider
from app.models.model import ModelResponse
from app.services.gemini_inspection_analyzer import GeminiInspectionAnalyzer


class FakeModelProvider:
    def __init__(self, output: str):
        self.output = output
        self.last_prompt = ""

    @property
    def name(self):
        return "fake-model"

    @property
    def capabilities(self):
        return ()

    def generate(self, request):
        self.last_prompt = request.prompt
        return ModelResponse(
            output=self.output,
            model_name=self.name,
        )


def test_analyzer_extracts_structured_findings():
    provider = FakeModelProvider(
        "- finding: Emergency stop failed. | severity: high | page: 4"
    )

    findings = GeminiInspectionAnalyzer(provider).analyze(
        "The emergency stop was found to be non-functional."
    )

    assert len(findings) == 1
    assert findings[0].finding == "Emergency stop failed."
    assert findings[0].severity == "high"
    assert findings[0].page_number == 4


def test_analyzer_includes_sop_evidence_in_prompt():
    provider = FakeModelProvider(
        "- finding: Guarding is damaged. | severity: medium"
    )

    GeminiInspectionAnalyzer(provider).analyze(
        "Guarding was damaged.",
        supporting_evidence=("SOP requires intact guarding.",),
    )

    assert "SOP requires intact guarding." in provider.last_prompt


def test_analyzer_instructs_model_not_to_invent_facts():
    provider = FakeModelProvider(
        "- finding: Belt wear observed. | severity: low"
    )

    GeminiInspectionAnalyzer(provider).analyze(
        "Belt wear observed."
    )

    assert "Do not invent findings, severity, or page numbers." in provider.last_prompt


def test_analyzer_rejects_empty_inspection():
    provider = FakeModelProvider("")

    try:
        GeminiInspectionAnalyzer(provider).analyze(" ")
    except ValueError as exc:
        assert str(exc) == "inspection_text must not be empty"
    else:
        raise AssertionError("Expected ValueError")


def test_analyzer_uses_model_output_for_extraction():
    provider = FakeModelProvider(
        """
- finding: Alignment is outside tolerance. | severity: medium | page: 2
- finding: Minor surface wear. | severity: low | page: 5
"""
    )

    findings = GeminiInspectionAnalyzer(provider).analyze(
        "Inspection report content."
    )

    assert [finding.severity for finding in findings] == [
        "medium",
        "low",
    ]

def test_analyzer_returns_no_findings_when_model_finds_none():
    provider = FakeModelProvider("")

    findings = GeminiInspectionAnalyzer(provider).analyze(
        "This is a resume describing software engineering experience."
    )

    assert findings == ()
    assert "return an empty response" in provider.last_prompt
    assert "Do not create a placeholder finding." in provider.last_prompt
