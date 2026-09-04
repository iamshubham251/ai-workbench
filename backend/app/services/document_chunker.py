"""Split normalized document content into searchable chunks."""

from dataclasses import dataclass

from app.models.document_chunk import DocumentChunk
from app.models.document_content import DocumentContent


@dataclass(frozen=True)
class DocumentChunkingConfig:
    """Configuration controlling document chunking."""

    max_characters: int = 1200
    overlap_characters: int = 200

    def __post_init__(self) -> None:
        if self.max_characters < 1:
            raise ValueError("max_characters must be positive")

        if self.overlap_characters < 0:
            raise ValueError("overlap_characters must not be negative")

        if self.overlap_characters >= self.max_characters:
            raise ValueError(
                "overlap_characters must be smaller than max_characters"
            )


class DocumentChunker:
    """Create page-aware, section-aware chunks from normalized content."""

    def __init__(
        self,
        config: DocumentChunkingConfig | None = None,
    ) -> None:
        self.config = config or DocumentChunkingConfig()

    def chunk(
        self,
        content: DocumentContent,
    ) -> tuple[DocumentChunk, ...]:
        """Split normalized document content into searchable chunks."""
        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for page_number, page_text in enumerate(content.pages, start=1):
            if not page_text.strip():
                continue

            section_title = self._section_for_page(
                content,
                page_number,
            )

            page_chunks = self._split_text(page_text)

            for text in page_chunks:
                chunks.append(
                    DocumentChunk(
                        document_id=content.document_id,
                        chunk_index=chunk_index,
                        text=text,
                        page_numbers=(page_number,),
                        section_title=section_title,
                    )
                )
                chunk_index += 1

        return tuple(chunks)

    def _split_text(self, text: str) -> list[str]:
        """Split text into overlapping character-based chunks."""
        normalized = " ".join(text.split())

        if not normalized:
            return []

        max_chars = self.config.max_characters
        overlap = self.config.overlap_characters

        if len(normalized) <= max_chars:
            return [normalized]

        chunks: list[str] = []
        start = 0

        while start < len(normalized):
            end = min(start + max_chars, len(normalized))

            if end < len(normalized):
                boundary = normalized.rfind(" ", start, end)

                if boundary > start:
                    end = boundary

            chunk = normalized[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(normalized):
                break

            next_start = end - overlap

            if next_start <= start:
                next_start = end

            while (
                next_start < len(normalized)
                and normalized[next_start].isspace()
            ):
                next_start += 1

            start = next_start

        return chunks

    @staticmethod
    def _section_for_page(
        content: DocumentContent,
        page_number: int,
    ) -> str | None:
        """Find the section associated with a page."""
        for section in content.sections:
            if page_number in section.page_numbers:
                return section.title

        return None