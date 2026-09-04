from uuid import uuid4

import pytest

from app.models.pdf_processing import PdfPage, PdfProcessingResult


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
