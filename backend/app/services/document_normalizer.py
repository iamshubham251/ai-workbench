"""Normalize processed PDF content for downstream AI workflows."""

import re

from app.models.document_content import DocumentContent, DocumentSection
from app.models.pdf_processing import PdfProcessingResult


class DocumentNormalizer:
    """Convert PDF processing output into clean document content."""

    def normalize(
        self,
        result: PdfProcessingResult,
    ) -> DocumentContent:
        """Normalize page text and detect simple document sections."""
        normalized_pages = tuple(
            self._normalize_text(page.text)
            for page in result.pages
        )

        sections = self._detect_sections(normalized_pages)

        return DocumentContent(
            document_id=result.document_id,
            pages=normalized_pages,
            sections=sections,
            warnings=result.warnings,
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize whitespace without changing document meaning."""
        text = text.replace("\x00", " ")
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        lines = [
            re.sub(r"[ \t]+", " ", line).strip()
            for line in text.split("\n")
        ]

        normalized_lines: list[str] = []
        previous_blank = False

        for line in lines:
            if not line:
                if not previous_blank:
                    normalized_lines.append("")
                previous_blank = True
                continue

            normalized_lines.append(line)
            previous_blank = False

        return "\n".join(normalized_lines).strip()

    @classmethod
    def _detect_sections(
        cls,
        pages: tuple[str, ...],
    ) -> tuple[DocumentSection, ...]:
        """Detect simple heading-based sections across normalized pages."""
        sections: list[DocumentSection] = []

        current_title: str | None = None
        current_lines: list[str] = []
        current_pages: list[int] = []

        for page_number, page_text in enumerate(pages, start=1):
            if not page_text:
                continue

            for line in page_text.splitlines():
                if cls._is_heading(line):
                    if current_title is not None and current_lines:
                        sections.append(
                            DocumentSection(
                                title=current_title,
                                text="\n".join(current_lines).strip(),
                                page_numbers=tuple(current_pages),
                            )
                        )

                    current_title = line.strip()
                    current_lines = []
                    current_pages = [page_number]
                    continue

                if current_title is not None:
                    current_lines.append(line)

                    if page_number not in current_pages:
                        current_pages.append(page_number)

        if current_title is not None and current_lines:
            sections.append(
                DocumentSection(
                    title=current_title,
                    text="\n".join(current_lines).strip(),
                    page_numbers=tuple(current_pages),
                )
            )

        return tuple(sections)

    @staticmethod
    def _is_heading(line: str) -> bool:
        """Identify conservative heading candidates."""
        stripped = line.strip()

        if not stripped:
            return False

        if len(stripped) > 120:
            return False

        if stripped.endswith((".", ",", ";", ":")):
            return False

        words = stripped.split()

        if len(words) > 12:
            return False

        if re.match(r"^(?:\d+(?:\.\d+)*|[A-Z])[\)\.\-]\s+\S+", stripped):
            return True

        if stripped.isupper() and len(words) <= 10:
            return True

        return False