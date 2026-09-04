"""Tests for PDF page rendering."""

from datetime import datetime, timezone
from uuid import uuid4

import pymupdf
import pytest

from app.models.document import Document
from app.services.pdf_renderer import (
    PdfRenderingError,
    PyMuPdfRenderer,
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
    """Create a small valid PDF for renderer tests."""
    pdf = pymupdf.open()

    for page_number in range(1, page_count + 1):
        page = pdf.new_page()
        page.insert_text(
            (72, 72),
            f"Test page {page_number}",
        )

    pdf.save(path)
    pdf.close()


def test_renderer_rejects_non_positive_dpi() -> None:
    with pytest.raises(ValueError, match="dpi must be positive"):
        PyMuPdfRenderer(dpi=0)


def test_renderer_rejects_zero_page_number(tmp_path) -> None:
    pdf_path = tmp_path / "test.pdf"
    create_pdf(pdf_path)

    renderer = PyMuPdfRenderer()
    document = create_document(str(pdf_path))

    with pytest.raises(
        ValueError,
        match="page_number must be one-based",
    ):
        renderer.render_page(document, 0)


def test_renderer_rejects_missing_pdf(tmp_path) -> None:
    renderer = PyMuPdfRenderer()

    document = create_document(
        str(tmp_path / "missing.pdf")
    )

    with pytest.raises(
        PdfRenderingError,
        match="PDF source is unavailable",
    ):
        renderer.render_page(document, 1)


def test_renderer_rejects_page_outside_pdf(tmp_path) -> None:
    pdf_path = tmp_path / "test.pdf"
    create_pdf(pdf_path, page_count=1)

    renderer = PyMuPdfRenderer()
    document = create_document(str(pdf_path))

    with pytest.raises(
        PdfRenderingError,
        match="PDF does not contain page 2",
    ):
        renderer.render_page(document, 2)


def test_renderer_returns_png_bytes(tmp_path) -> None:
    pdf_path = tmp_path / "test.pdf"
    create_pdf(pdf_path)

    renderer = PyMuPdfRenderer()
    document = create_document(str(pdf_path))

    image = renderer.render_page(document, 1)

    assert isinstance(image, bytes)
    assert image.startswith(b"\x89PNG\r\n\x1a\n")


def test_renderer_can_render_specific_page(tmp_path) -> None:
    pdf_path = tmp_path / "test.pdf"
    create_pdf(pdf_path, page_count=3)

    renderer = PyMuPdfRenderer()
    document = create_document(str(pdf_path))

    image = renderer.render_page(document, 3)

    assert image.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(image) > 0