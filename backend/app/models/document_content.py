"""Domain types for normalized document content."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DocumentSection:
    """A logical section of normalized document content."""

    title: str
    text: str
    page_numbers: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")

        if not self.text.strip():
            raise ValueError("text must not be empty")

        if any(page_number < 1 for page_number in self.page_numbers):
            raise ValueError("page numbers must be one-based")


@dataclass(frozen=True)
class DocumentContent:
    """Normalized content produced from a processed document."""

    document_id: UUID
    pages: tuple[str, ...] = ()
    sections: tuple[DocumentSection, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def page_count(self) -> int:
        """Return the number of normalized pages."""
        return len(self.pages)

    @property
    def section_count(self) -> int:
        """Return the number of detected sections."""
        return len(self.sections)

    @property
    def full_text(self) -> str:
        """Return all normalized page text as one document."""
        return "\n\n".join(
            page.strip()
            for page in self.pages
            if page.strip()
        )