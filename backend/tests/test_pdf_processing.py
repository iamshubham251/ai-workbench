from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.models.pdf_processing import (
    PdfContentType,
    PdfPage,
    PdfProcessingResult,
)
from app.models.document import Document
from app.services.pypdf_processor import PdfProcessingError, PypdfProcessor


def build_pdf(page_texts: list[str]) -> bytes:
    """Build a minimal text PDF fixture without adding a PDF-writing dependency."""
    page_ids = list(range(3, 3 + len(page_texts)))
    font_id = 3 + len(page_texts)
    content_ids = list(range(font_id + 1, font_id + 1 + len(page_texts)))

    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] /Count {len(page_ids)} >>".encode(),
        font_id: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }

    for page_id, content_id, text in zip(page_ids, content_ids, page_texts):
        stream = (
            f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
            if text
            else b""
        )

        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode()

        objects[content_id] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode()
            + stream
            + b"\nendstream"
        )

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for object_id in range(1, max(objects) + 1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode())
        output.extend(objects[object_id])
        output.extend(b"\nendobj\n")

    xref_offset = len(output)

    output.extend(f"xref\n0 {len(offsets)}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    output.extend(
        b"".join(
            f"{offset:010d} 00000 n \n".encode()
            for offset in offsets[1:]
        )
    )

    output.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode()
    )

    return bytes(output)


def make_document(storage_path: str) -> Document:
    now = datetime.now(timezone.utc)

    return Document(
        id=uuid4(),
        original_filename="report.pdf",
        stored_filename="report.pdf",
        content_type="application/pdf",
        extension=".pdf",
        size_bytes=0,
        status="uploaded",
        storage_path=storage_path,
        created_at=now,
        updated_at=now,
    )


def test_pdf_processing_result_counts_pages():
    result = PdfProcessingResult(
        document_id=uuid4(),
        pages=(PdfPage(page_number=1, text="First page"),),
        warnings=("Metadata was unavailable",),
    )

    assert result.page_count == 1
    assert result.pages[0].text == "First page"
    assert result.warnings == ("Metadata was unavailable",)


def test_pdf_page_requires_one_based_page_numbers():
    with pytest.raises(ValueError, match="one-based"):
        PdfPage(page_number=0, text="Invalid")


def test_pypdf_processor_extracts_text_in_page_order(tmp_path):
    pdf_path = tmp_path / "report.pdf"
    pdf_path.write_bytes(build_pdf(["First page", "Second page"]))
    document = make_document(str(pdf_path))

    result = PypdfProcessor().process(document)

    assert result.document_id == document.id
    assert result.page_count == 2
    assert [page.page_number for page in result.pages] == [1, 2]
    assert "First page" in result.pages[0].text
    assert "Second page" in result.pages[1].text


def test_pypdf_processor_returns_empty_text_for_empty_page(tmp_path):
    pdf_path = tmp_path / "empty.pdf"
    pdf_path.write_bytes(build_pdf([""]))

    result = PypdfProcessor().process(make_document(str(pdf_path)))

    assert result.pages == (PdfPage(page_number=1, text=""),)


def test_pypdf_processor_classifies_text_pdf(tmp_path):
    pdf_path = tmp_path / "text.pdf"
    pdf_path.write_bytes(
        build_pdf(
            [
                "This page contains meaningful extracted text.",
                "This second page also contains meaningful text.",
            ]
        )
    )

    result = PypdfProcessor().process(make_document(str(pdf_path)))

    assert result.content_type == PdfContentType.TEXT


def test_pypdf_processor_classifies_scanned_like_pdf(tmp_path):
    pdf_path = tmp_path / "scanned.pdf"
    pdf_path.write_bytes(
        build_pdf(
            [
                "This page contains meaningful extracted text.",
                "",
                "",
                "",
                "",
                "",
            ]
        )
    )

    result = PypdfProcessor().process(make_document(str(pdf_path)))

    assert result.content_type == PdfContentType.SCANNED


def test_pypdf_processor_classifies_mixed_pdf(tmp_path):
    pdf_path = tmp_path / "mixed.pdf"
    pdf_path.write_bytes(
        build_pdf(
            [
                "This page contains meaningful extracted text.",
                "",
                "This page also contains meaningful extracted text.",
            ]
        )
    )

    result = PypdfProcessor().process(make_document(str(pdf_path)))

    assert result.content_type == PdfContentType.MIXED


def test_pypdf_processor_rejects_missing_source(tmp_path):
    document = make_document(str(tmp_path / "missing.pdf"))

    with pytest.raises(PdfProcessingError, match="unavailable"):
        PypdfProcessor().process(document)