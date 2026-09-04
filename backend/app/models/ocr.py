"""Domain types for OCR processing."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class OcrPage:
    """OCR text produced for one one-based PDF page."""

    page_number: int
    text: str
    confidence: float | None = None

    def __post_init__(self) -> None:
        if self.page_number < 1:
            raise ValueError("page_number must be one-based")

        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass(frozen=True)
class OcrProcessingResult:
    """The OCR result for a document."""

    document_id: UUID
    pages: tuple[OcrPage, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def text_page_count(self) -> int:
        """Number of OCR pages containing meaningful text."""
        return sum(bool(page.text.strip()) for page in self.pages)