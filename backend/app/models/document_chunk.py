"""Domain types for RAG document chunks."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DocumentChunk:
    """A searchable chunk of normalized document content."""

    document_id: UUID
    chunk_index: int
    text: str
    page_numbers: tuple[int, ...] = ()
    section_title: str | None = None

    def __post_init__(self) -> None:
        if self.chunk_index < 0:
            raise ValueError("chunk_index must not be negative")

        if not self.text.strip():
            raise ValueError("text must not be empty")

        if any(page_number < 1 for page_number in self.page_numbers):
            raise ValueError("page numbers must be one-based")

        if self.section_title is not None and not self.section_title.strip():
            raise ValueError("section_title must not be empty")

    @property
    def character_count(self) -> int:
        """Return the number of characters in the chunk."""
        return len(self.text)

    @property
    def word_count(self) -> int:
        """Return the number of whitespace-separated words."""
        return len(self.text.split())