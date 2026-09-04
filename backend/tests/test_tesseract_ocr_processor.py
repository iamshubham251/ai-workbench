"""Tests for Tesseract-backed OCR processing."""

from datetime import datetime, timezone
from uuid import uuid4

import pymupdf
import pytest

from app.models.document import Document
from app.models.ocr import OcrProcessingResult
from app.services.ocr_processor import OcrProcessingError
from app.services.tesseract_ocr_processor import (
    TesseractOcrProcessor,
)


def create_document(storage_path: str) -> Document:
    """Create a document pointing at the supplied test PDF."""
    now = datetime.now(timezone.utc)

    return Document(
        id=uuid4(),
        original_filename="test.pdf",
        stored_filename="test.pdf",
        content_type="application/pdf",
        extension=".pdf",
        size_bytes=100,
        status="uploaded",
        storage_path=storage_path,
        created_at=now,
        updated_at=now,
    )


def create_pdf(path, page_count: int = 1) -> None:
    """Create a small PDF for OCR tests."""
    pdf = pymupdf.open()

    for page_number in range(1, page_count + 1):
        page = pdf.new_page()
        page.insert_text(
            (72, 72),
            f"Test page {page_number}",
        )

    pdf.save(path)
    pdf.close()


def test_processor_rejects_non_positive_dpi() -> None:
    with pytest.raises(ValueError, match="dpi must be positive"):
        TesseractOcrProcessor(dpi=0)


def test_processor_rejects_empty_language() -> None:
    with pytest.raises(ValueError, match="language must not be empty"):
        TesseractOcrProcessor(language="   ")


def test_processor_rejects_missing_tesseract() -> None:
    with pytest.raises(
        OcrProcessingError,
        match="Tesseract executable could not be found",
    ):
        TesseractOcrProcessor(
            tesseract_cmd="C:\\does-not-exist\\tesseract.exe",
        )


def test_processor_rejects_missing_pdf(tmp_path) -> None:
    processor = TesseractOcrProcessor()

    document = create_document(
        str(tmp_path / "missing.pdf"),
    )

    with pytest.raises(
        OcrProcessingError,
        match="OCR source document is unavailable",
    ):
        processor.process(document)


def test_processor_returns_result_for_pdf(tmp_path) -> None:
    pdf_path = tmp_path / "test.pdf"
    create_pdf(pdf_path)

    processor = TesseractOcrProcessor()

    document = create_document(str(pdf_path))

    result = processor.process(document)

    assert isinstance(result, OcrProcessingResult)
    assert result.document_id == document.id
    assert result.page_count == 1
    assert len(result.pages) == 1


def test_processor_processes_multiple_pages(tmp_path) -> None:
    pdf_path = tmp_path / "test.pdf"
    create_pdf(pdf_path, page_count=3)

    processor = TesseractOcrProcessor()

    document = create_document(str(pdf_path))

    result = processor.process(document)

    assert result.page_count == 3
    assert [page.page_number for page in result.pages] == [1, 2, 3]


def test_processor_produces_confidence_or_none(tmp_path) -> None:
    pdf_path = tmp_path / "test.pdf"
    create_pdf(pdf_path)

    processor = TesseractOcrProcessor()

    document = create_document(str(pdf_path))

    result = processor.process(document)

    assert len(result.pages) == 1

    confidence = result.pages[0].confidence

    assert confidence is None or 0.0 <= confidence <= 1.0