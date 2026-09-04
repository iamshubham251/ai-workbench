import pytest

from app.models.pdf_processing import PdfContentType, PdfPage
from app.services.pdf_content_detector import (
    PdfContentDetectionConfig,
    PdfContentDetector,
)


def page(number: int, text: str) -> PdfPage:
    return PdfPage(page_number=number, text=text)


def test_empty_document_is_classified_as_empty():
    detector = PdfContentDetector()

    assert detector.classify(()) == PdfContentType.EMPTY


def test_pages_without_meaningful_text_are_classified_as_empty():
    detector = PdfContentDetector()

    pages = (
        page(1, ""),
        page(2, "   "),
        page(3, "\n\t"),
    )

    assert detector.classify(pages) == PdfContentType.EMPTY


def test_text_document_is_classified_as_text():
    detector = PdfContentDetector()

    pages = (
        page(1, "This page contains meaningful extracted text."),
        page(2, "This is another page with sufficient textual content."),
    )

    assert detector.classify(pages) == PdfContentType.TEXT


def test_mixed_document_is_classified_as_mixed():
    detector = PdfContentDetector()

    pages = (
        page(1, "This page contains meaningful extracted text."),
        page(2, ""),
        page(3, "This page also contains meaningful extracted text."),
    )

    assert detector.classify(pages) == PdfContentType.MIXED


def test_low_text_ratio_is_classified_as_scanned():
    detector = PdfContentDetector()

    pages = (
        page(1, "This page contains meaningful extracted text."),
        page(2, ""),
        page(3, ""),
        page(4, ""),
        page(5, ""),
        page(6, ""),
    )

    assert detector.classify(pages) == PdfContentType.SCANNED


def test_short_text_is_not_considered_meaningful():
    detector = PdfContentDetector()

    pages = (
        page(1, "Title"),
        page(2, "Signature"),
    )

    assert detector.classify(pages) == PdfContentType.EMPTY


def test_detector_thresholds_are_configurable():
    config = PdfContentDetectionConfig(
        min_meaningful_characters=5,
        min_meaningful_words=1,
        min_text_page_ratio=0.5,
    )
    detector = PdfContentDetector(config)

    pages = (
        page(1, "Hello"),
        page(2, ""),
    )

    assert detector.classify(pages) == PdfContentType.MIXED


def test_invalid_character_threshold_is_rejected():
    with pytest.raises(ValueError, match="min_meaningful_characters"):
        PdfContentDetectionConfig(min_meaningful_characters=0)


def test_invalid_word_threshold_is_rejected():
    with pytest.raises(ValueError, match="min_meaningful_words"):
        PdfContentDetectionConfig(min_meaningful_words=0)


def test_invalid_page_ratio_is_rejected():
    with pytest.raises(ValueError, match="min_text_page_ratio"):
        PdfContentDetectionConfig(min_text_page_ratio=0)


def test_page_ratio_above_one_is_rejected():
    with pytest.raises(ValueError, match="min_text_page_ratio"):
        PdfContentDetectionConfig(min_text_page_ratio=1.1)