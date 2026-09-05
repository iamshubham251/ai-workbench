"""Extract structured inspection findings from model output."""

import re

from app.models.approval_workflow import InspectionFinding


class InspectionFindingExtractionError(ValueError):
    """Raised when inspection findings cannot be extracted."""


class InspectionFindingExtractor:
    """Parse a strict line-oriented finding format."""

    _PATTERN = re.compile(
        r"^\s*-\s*finding:\s*(?P<finding>.+?)"
        r"(?:\s*\|\s*severity:\s*(?P<severity>[^|]+?))?"
        r"(?:\s*\|\s*page:\s*(?P<page>\d+))?\s*$",
        re.IGNORECASE,
    )

    def extract(self, text: str) -> tuple[InspectionFinding, ...]:
        if not text.strip():
            raise InspectionFindingExtractionError(
                "inspection output must not be empty"
            )

        findings: list[InspectionFinding] = []

        for line in text.splitlines():
            match = self._PATTERN.match(line)
            if not match:
                continue

            finding = match.group("finding").strip()
            severity = (match.group("severity") or "").strip()
            page_value = match.group("page")
            page_number = int(page_value) if page_value else None

            findings.append(
                InspectionFinding(
                    finding=finding,
                    severity=severity,
                    page_number=page_number,
                )
            )

        if not findings:
            raise InspectionFindingExtractionError(
                "no structured inspection findings were found"
            )

        return tuple(findings)
