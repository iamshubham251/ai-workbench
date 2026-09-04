"""Tests for the PDF processing pipeline."""

from datetime import datetime, timezone
from uuid import uuid4

from app.models.document import Document
from app.models.ocr import OcrPage, OcrProcessingResult
from app.models.pdf_processing import (
    PdfContentType,
    PdfPage,
    PdfProcessingResult,
)
from app.services.pdf_processing_pipeline import PdfProcessingPipeline


def create_document() -> Document:
    """Create a document for pipeline tests."""
    now = datetime.now(timezone.utc)

    return Document(
        id=uuid4(),
        original_filename="test.pdf",
        stored_filename="test.pdf",
        content_type="application/pdf",
        extension=".pdf",
        size_bytes=100,
        status="uploaded",
        storage_path="test.pdf",
        created_at=now,
        updated_at=now,
    )


class FakePdfProcessor:
    """Fake PDF processor returning a predefined result."""

    def __init__(self, result: PdfProcessingResult) -> None:
        self.result = result
        self.calls = 0

    def process(self, document: Document) -> PdfProcessingResult:
        self.calls += 1
        return self.result


class FakeOcrProcessor:
    """Fake OCR processor returning a predefined result."""

    def __init__(self, result: OcrProcessingResult) -> None:
        self.result = result
        self.calls = 0

    def process(self, document: Document) -> OcrProcessingResult:
        self.calls += 1
        return self.result


def create_extracted_result(
    document: Document,
    content_type: PdfContentType,
    pages: tuple[PdfPage, ...],
    warnings: tuple[str, ...] = (),
) -> PdfProcessingResult:
    """Create a PDF extraction result."""
    return PdfProcessingResult(
        document_id=document.id,
        pages=pages,
        warnings=warnings,
        content_type=content_type,
    )


def create_ocr_result(
    document: Document,
    pages: tuple[OcrPage, ...],
    warnings: tuple[str, ...] = (),
) -> OcrProcessingResult:
    """Create an OCR result."""
    return OcrProcessingResult(
        document_id=document.id,
        pages=pages,
        warnings=warnings,
    )


def test_text_pdf_skips_ocr() -> None:
    document = create_document()

    extracted = create_extracted_result(
        document,
        PdfContentType.TEXT,
        (
            PdfPage(
                page_number=1,
                text="Embedded PDF text",
            ),
        ),
    )

    pdf_processor = FakePdfProcessor(extracted)

    ocr_processor = FakeOcrProcessor(
        create_ocr_result(
            document,
            (
                OcrPage(
                    page_number=1,
                    text="OCR text",
                ),
            ),
        )
    )

    pipeline = PdfProcessingPipeline(
        pdf_processor,
        ocr_processor,
    )

    result = pipeline.process(document)

    assert result == extracted
    assert pdf_processor.calls == 1
    assert ocr_processor.calls == 0


def test_empty_pdf_skips_ocr() -> None:
    document = create_document()

    extracted = create_extracted_result(
        document,
        PdfContentType.EMPTY,
        (),
    )

    pdf_processor = FakePdfProcessor(extracted)
    ocr_processor = FakeOcrProcessor(
        create_ocr_result(document, ())
    )

    pipeline = PdfProcessingPipeline(
        pdf_processor,
        ocr_processor,
    )

    result = pipeline.process(document)

    assert result == extracted
    assert pdf_processor.calls == 1
    assert ocr_processor.calls == 0


def test_scanned_pdf_uses_ocr_pages() -> None:
    document = create_document()

    extracted = create_extracted_result(
        document,
        PdfContentType.SCANNED,
        (
            PdfPage(
                page_number=1,
                text="",
            ),
            PdfPage(
                page_number=2,
                text="",
            ),
        ),
        warnings=("Extraction warning",),
    )

    ocr_result = create_ocr_result(
        document,
        (
            OcrPage(
                page_number=1,
                text="OCR page one",
                confidence=0.95,
            ),
            OcrPage(
                page_number=2,
                text="OCR page two",
                confidence=0.90,
            ),
        ),
        warnings=("OCR warning",),
    )

    pdf_processor = FakePdfProcessor(extracted)
    ocr_processor = FakeOcrProcessor(ocr_result)

    pipeline = PdfProcessingPipeline(
        pdf_processor,
        ocr_processor,
    )

    result = pipeline.process(document)

    assert result.content_type == PdfContentType.SCANNED
    assert result.page_count == 2
    assert [page.text for page in result.pages] == [
        "OCR page one",
        "OCR page two",
    ]
    assert result.warnings == (
        "Extraction warning",
        "OCR warning",
    )
    assert pdf_processor.calls == 1
    assert ocr_processor.calls == 1


def test_mixed_pdf_preserves_existing_text_and_fills_empty_pages() -> None:
    document = create_document()

    extracted = create_extracted_result(
        document,
        PdfContentType.MIXED,
        (
            PdfPage(
                page_number=1,
                text="Existing embedded text",
            ),
            PdfPage(
                page_number=2,
                text="",
            ),
            PdfPage(
                page_number=3,
                text="Another embedded page",
            ),
        ),
    )

    ocr_result = create_ocr_result(
        document,
        (
            OcrPage(
                page_number=1,
                text="OCR should not replace this",
            ),
            OcrPage(
                page_number=2,
                text="OCR fills this page",
            ),
            OcrPage(
                page_number=3,
                text="OCR should not replace this either",
            ),
        ),
    )

    pdf_processor = FakePdfProcessor(extracted)
    ocr_processor = FakeOcrProcessor(ocr_result)

    pipeline = PdfProcessingPipeline(
        pdf_processor,
        ocr_processor,
    )

    result = pipeline.process(document)

    assert result.content_type == PdfContentType.MIXED
    assert [page.text for page in result.pages] == [
        "Existing embedded text",
        "OCR fills this page",
        "Another embedded page",
    ]
    assert pdf_processor.calls == 1
    assert ocr_processor.calls == 1


def test_mixed_pdf_keeps_empty_page_when_ocr_page_is_missing() -> None:
    document = create_document()

    extracted = create_extracted_result(
        document,
        PdfContentType.MIXED,
        (
            PdfPage(
                page_number=1,
                text="",
            ),
            PdfPage(
                page_number=2,
                text="Embedded text",
            ),
        ),
    )

    ocr_result = create_ocr_result(
        document,
        (
            OcrPage(
                page_number=2,
                text="OCR page two",
            ),
        ),
    )

    pipeline = PdfProcessingPipeline(
        FakePdfProcessor(extracted),
        FakeOcrProcessor(ocr_result),
    )

    result = pipeline.process(document)

    assert [page.text for page in result.pages] == [
        "",
        "Embedded text",
    ]


def test_mixed_pdf_combines_warnings() -> None:
    document = create_document()

    extracted = create_extracted_result(
        document,
        PdfContentType.MIXED,
        (
            PdfPage(
                page_number=1,
                text="",
            ),
        ),
        warnings=("PDF warning",),
    )

    ocr_result = create_ocr_result(
        document,
        (
            OcrPage(
                page_number=1,
                text="OCR text",
            ),
        ),
        warnings=("OCR warning",),
    )

    pipeline = PdfProcessingPipeline(
        FakePdfProcessor(extracted),
        FakeOcrProcessor(ocr_result),
    )

    result = pipeline.process(document)

    assert result.warnings == (
        "PDF warning",
        "OCR warning",
    )