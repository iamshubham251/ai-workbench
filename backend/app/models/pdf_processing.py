"""Domain types for PDF text extraction and classification."""

from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class PdfContentType(str, Enum):
    """Classification of the textual content available in a PDF."""

    TEXT = "text"
    SCANNED = "scanned"
    MIXED = "mixed"
    EMPTY = "empty"


@dataclass(frozen=True)
class PdfPage:
    """Text extracted from one one-based PDF page."""

    page_number: int
    text: str

    def __post_init__(self) -> None:
        if self.page_number < 1:
            raise ValueError("page_number must be one-based")


@dataclass(frozen=True)
class PdfProcessingResult:
    """The text-extraction and content-classification result for a PDF."""

    document_id: UUID
    pages: tuple[PdfPage, ...] = ()
    warnings: tuple[str, ...] = ()
    content_type: PdfContentType = PdfContentType.EMPTY

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def text_page_count(self) -> int:
        """Number of pages containing meaningful extracted text."""
        return sum(bool(page.text.strip()) for page in self.pages)

    @property
    def empty_page_count(self) -> int:
        """Number of pages without meaningful extracted text."""
        return self.page_count - self.text_page_count