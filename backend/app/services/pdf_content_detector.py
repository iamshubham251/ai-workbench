"""Production-grade PDF content classification."""

from dataclasses import dataclass

from app.models.pdf_processing import PdfContentType, PdfPage


@dataclass(frozen=True)
class PdfContentDetectionConfig:
    """Configuration controlling PDF content classification."""

    min_meaningful_characters: int = 20
    min_meaningful_words: int = 3
    min_text_page_ratio: float = 0.20

    def __post_init__(self) -> None:
        if self.min_meaningful_characters < 1:
            raise ValueError("min_meaningful_characters must be positive")

        if self.min_meaningful_words < 1:
            raise ValueError("min_meaningful_words must be positive")

        if not 0.0 < self.min_text_page_ratio <= 1.0:
            raise ValueError(
                "min_text_page_ratio must be greater than 0 and at most 1"
            )


class PdfContentDetector:
    """Classify a PDF based on the amount of meaningful extracted text."""

    def __init__(
        self,
        config: PdfContentDetectionConfig | None = None,
    ) -> None:
        self.config = config or PdfContentDetectionConfig()

    def classify(self, pages: tuple[PdfPage, ...]) -> PdfContentType:
        """Classify extracted PDF pages as text, scanned, mixed, or empty."""
        if not pages:
            return PdfContentType.EMPTY

        meaningful_pages = sum(
            self._has_meaningful_text(page.text)
            for page in pages
        )

        if meaningful_pages == 0:
            return PdfContentType.EMPTY

        if meaningful_pages == len(pages):
            return PdfContentType.TEXT

        text_page_ratio = meaningful_pages / len(pages)

        if text_page_ratio >= self.config.min_text_page_ratio:
            return PdfContentType.MIXED

        return PdfContentType.SCANNED

    def _has_meaningful_text(self, text: str) -> bool:
        """Determine whether extracted page text is substantial enough."""
        normalized = " ".join(text.split())

        if len(normalized) < self.config.min_meaningful_characters:
            return False

        words = normalized.split()

        return len(words) >= self.config.min_meaningful_words