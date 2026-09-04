import pytest
from uuid import uuid4

from app.models.ocr import OcrPage, OcrProcessingResult


def test_ocr_page_requires_one_based_page_numbers():
    with pytest.raises(ValueError, match="one-based"):
        OcrPage(page_number=0, text="Invalid")


def test_ocr_page_accepts_missing_confidence():
    page = OcrPage(page_number=1, text="Recognized text")

    assert page.page_number == 1
    assert page.text == "Recognized text"
    assert page.confidence is None


def test_ocr_page_accepts_valid_confidence():
    page = OcrPage(
        page_number=1,
        text="Recognized text",
        confidence=0.95,
    )

    assert page.confidence == 0.95


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_ocr_page_rejects_invalid_confidence(confidence):
    with pytest.raises(ValueError, match="confidence"):
        OcrPage(
            page_number=1,
            text="Recognized text",
            confidence=confidence,
        )


def test_ocr_processing_result_counts_pages():
    result = OcrProcessingResult(
        document_id=uuid4(),
        pages=(
            OcrPage(page_number=1, text="First page"),
            OcrPage(page_number=2, text="Second page"),
        ),
    )

    assert result.page_count == 2


def test_ocr_processing_result_counts_meaningful_text_pages():
    result = OcrProcessingResult(
        document_id=uuid4(),
        pages=(
            OcrPage(page_number=1, text="First page"),
            OcrPage(page_number=2, text=""),
            OcrPage(page_number=3, text="   "),
            OcrPage(page_number=4, text="Fourth page"),
        ),
    )

    assert result.text_page_count == 2


def test_ocr_processing_result_preserves_warnings():
    result = OcrProcessingResult(
        document_id=uuid4(),
        warnings=("Page 2 OCR confidence was low",),
    )

    assert result.warnings == ("Page 2 OCR confidence was low",)