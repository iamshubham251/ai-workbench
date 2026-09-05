import pytest

from app.models.approval_workflow import InspectionFinding
from app.services.inspection_finding_extractor import (
    InspectionFindingExtractionError,
    InspectionFindingExtractor,
)


def test_extracts_finding_with_all_fields():
    text = (
        "- finding: Emergency stop is not functional. "
        "| severity: high | page: 4"
    )

    findings = InspectionFindingExtractor().extract(text)

    assert findings == (
        InspectionFinding(
            finding="Emergency stop is not functional.",
            severity="high",
            page_number=4,
        ),
    )


def test_extracts_multiple_findings():
    text = """
- finding: Belt alignment is outside tolerance. | severity: medium | page: 2
- finding: Minor surface wear observed. | severity: low | page: 5
"""

    findings = InspectionFindingExtractor().extract(text)

    assert len(findings) == 2
    assert findings[0].severity == "medium"
    assert findings[1].severity == "low"


def test_page_and_severity_are_optional():
    findings = InspectionFindingExtractor().extract(
        "- finding: Guarding requires inspection."
    )

    assert findings[0].finding == "Guarding requires inspection."
    assert findings[0].severity == ""
    assert findings[0].page_number is None


def test_ignores_non_finding_lines():
    text = """
Inspection report:
The following issues were observed.

- finding: Emergency stop failed. | severity: high | page: 3

Recommendation: immediate action.
"""

    findings = InspectionFindingExtractor().extract(text)

    assert len(findings) == 1
    assert findings[0].finding == "Emergency stop failed."


def test_empty_output_is_rejected():
    with pytest.raises(
        InspectionFindingExtractionError,
        match="must not be empty",
    ):
        InspectionFindingExtractor().extract(" ")


def test_unstructured_output_is_rejected():
    with pytest.raises(
        InspectionFindingExtractionError,
        match="no structured inspection findings",
    ):
        InspectionFindingExtractor().extract(
            "The inspection found several problems."
        )
