"""Tests for document normalization."""

from uuid import uuid4

from app.models.document_content import DocumentContent
from app.models.pdf_processing import (
    PdfContentType,
    PdfPage,
    PdfProcessingResult,
)
from app.services.document_normalizer import DocumentNormalizer


def create_result(
    pages: tuple[PdfPage, ...],
    warnings: tuple[str, ...] = (),
) -> PdfProcessingResult:
    """Create a PDF processing result for normalization tests."""
    return PdfProcessingResult(
        document_id=uuid4(),
        pages=pages,
        warnings=warnings,
        content_type=PdfContentType.TEXT,
    )


def test_normalizer_returns_document_content() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text="Hello world",
            ),
        )
    )

    normalized = DocumentNormalizer().normalize(result)

    assert isinstance(normalized, DocumentContent)
    assert normalized.document_id == result.document_id


def test_normalizer_normalizes_whitespace() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text="  Hello   world  \r\n\r\n  This   is   text.  ",
            ),
        )
    )

    normalized = DocumentNormalizer().normalize(result)

    assert normalized.pages == (
        "Hello world\n\nThis is text.",
    )


def test_normalizer_removes_null_characters() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text="Hello\x00world",
            ),
        )
    )

    normalized = DocumentNormalizer().normalize(result)

    assert normalized.pages == (
        "Hello world",
    )


def test_normalizer_preserves_page_boundaries() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text="First page",
            ),
            PdfPage(
                page_number=2,
                text="Second page",
            ),
        )
    )

    normalized = DocumentNormalizer().normalize(result)

    assert normalized.page_count == 2
    assert normalized.pages == (
        "First page",
        "Second page",
    )


def test_full_text_joins_non_empty_pages() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text="First page",
            ),
            PdfPage(
                page_number=2,
                text="",
            ),
            PdfPage(
                page_number=3,
                text="Third page",
            ),
        )
    )

    normalized = DocumentNormalizer().normalize(result)

    assert normalized.full_text == "First page\n\nThird page"


def test_normalizer_detects_uppercase_heading() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text="INTRODUCTION\nThis is the introduction.",
            ),
        )
    )

    normalized = DocumentNormalizer().normalize(result)

    assert normalized.section_count == 1
    assert normalized.sections[0].title == "INTRODUCTION"
    assert normalized.sections[0].text == "This is the introduction."
    assert normalized.sections[0].page_numbers == (1,)


def test_normalizer_detects_numbered_heading() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text="1. Inspection Findings\nThe inspection identified several issues.",
            ),
        )
    )

    normalized = DocumentNormalizer().normalize(result)

    assert normalized.section_count == 1
    assert normalized.sections[0].title == "1. Inspection Findings"
    assert normalized.sections[0].text == (
        "The inspection identified several issues."
    )


def test_normalizer_tracks_section_across_pages() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text="INSPECTION FINDINGS\nIssue one was identified.",
            ),
            PdfPage(
                page_number=2,
                text="Issue two was identified.",
            ),
        )
    )

    normalized = DocumentNormalizer().normalize(result)

    assert normalized.section_count == 1
    assert normalized.sections[0].title == "INSPECTION FINDINGS"
    assert normalized.sections[0].text == (
        "Issue one was identified.\nIssue two was identified."
    )
    assert normalized.sections[0].page_numbers == (1, 2)


def test_normalizer_detects_multiple_sections() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text=(
                    "INTRODUCTION\n"
                    "This is the introduction.\n\n"
                    "FINDINGS\n"
                    "These are the findings."
                ),
            ),
        )
    )

    normalized = DocumentNormalizer().normalize(result)

    assert normalized.section_count == 2
    assert normalized.sections[0].title == "INTRODUCTION"
    assert normalized.sections[0].text == "This is the introduction."
    assert normalized.sections[1].title == "FINDINGS"
    assert normalized.sections[1].text == "These are the findings."


def test_normalizer_preserves_warnings() -> None:
    result = create_result(
        (
            PdfPage(
                page_number=1,
                text="Some content",
            ),
        ),
        warnings=("OCR warning",),
    )

    normalized = DocumentNormalizer().normalize(result)

    assert normalized.warnings == ("OCR warning",)