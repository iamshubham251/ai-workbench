"""Domain types for future PDF text extraction."""

from dataclasses import dataclass
from uuid import UUID


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
    """The text-extraction result for a stored PDF document."""

    document_id: UUID
    pages: tuple[PdfPage, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def page_count(self) -> int:
        return len(self.pages)
