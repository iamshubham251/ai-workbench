"""Tests for document chunking."""

from uuid import uuid4

import pytest

from app.models.document_chunk import DocumentChunk
from app.models.document_content import DocumentContent, DocumentSection
from app.services.document_chunker import (
    DocumentChunker,
    DocumentChunkingConfig,
)


def create_content(
    pages: tuple[str, ...],
    sections: tuple[DocumentSection, ...] = (),
) -> DocumentContent:
    """Create normalized document content for chunking tests."""
    return DocumentContent(
        document_id=uuid4(),
        pages=pages,
        sections=sections,
    )


def test_chunker_returns_document_chunks() -> None:
    content = create_content(
        ("This is a test document.",)
    )

    chunks = DocumentChunker().chunk(content)

    assert len(chunks) == 1
    assert isinstance(chunks[0], DocumentChunk)
    assert chunks[0].text == "This is a test document."


def test_chunker_preserves_document_id() -> None:
    document_id = uuid4()

    content = DocumentContent(
        document_id=document_id,
        pages=("Document content.",),
    )

    chunks = DocumentChunker().chunk(content)

    assert chunks[0].document_id == document_id


def test_chunker_assigns_sequential_indexes() -> None:
    content = create_content(
        (
            "First page content.",
            "Second page content.",
            "Third page content.",
        )
    )

    chunks = DocumentChunker().chunk(content)

    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]


def test_chunker_preserves_page_numbers() -> None:
    content = create_content(
        (
            "First page.",
            "Second page.",
        )
    )

    chunks = DocumentChunker().chunk(content)

    assert chunks[0].page_numbers == (1,)
    assert chunks[1].page_numbers == (2,)


def test_chunker_skips_empty_pages() -> None:
    content = create_content(
        (
            "First page.",
            "",
            "Third page.",
        )
    )

    chunks = DocumentChunker().chunk(content)

    assert len(chunks) == 2
    assert [chunk.page_numbers for chunk in chunks] == [
        (1,),
        (3,),
    ]


def test_chunker_normalizes_whitespace() -> None:
    content = create_content(
        (
            "  This   is\n\n a   document.  ",
        )
    )

    chunks = DocumentChunker().chunk(content)

    assert chunks[0].text == "This is a document."


def test_chunker_preserves_section_title() -> None:
    section = DocumentSection(
        title="INSPECTION FINDINGS",
        text="The inspection identified an issue.",
        page_numbers=(1,),
    )

    content = create_content(
        (
            "The inspection identified an issue.",
        ),
        sections=(section,),
    )

    chunks = DocumentChunker().chunk(content)

    assert chunks[0].section_title == "INSPECTION FINDINGS"


def test_chunker_uses_none_when_page_has_no_section() -> None:
    content = create_content(
        (
            "Content without a detected section.",
        )
    )

    chunks = DocumentChunker().chunk(content)

    assert chunks[0].section_title is None


def test_chunker_splits_long_text() -> None:
    content = create_content(
        (
            " ".join(["word"] * 100),
        )
    )

    chunker = DocumentChunker(
        DocumentChunkingConfig(
            max_characters=100,
            overlap_characters=20,
        )
    )

    chunks = chunker.chunk(content)

    assert len(chunks) > 1
    assert all(
        len(chunk.text) <= 100
        for chunk in chunks
    )


def test_chunker_creates_overlapping_chunks() -> None:
    words = [f"word{i}" for i in range(1, 31)]

    content = create_content(
        (" ".join(words),)
    )

    chunker = DocumentChunker(
        DocumentChunkingConfig(
            max_characters=50,
            overlap_characters=15,
        )
    )

    chunks = chunker.chunk(content)

    assert len(chunks) > 1

    first_words = set(chunks[0].text.split())
    second_words = set(chunks[1].text.split())

    assert first_words.intersection(second_words)


def test_chunker_rejects_invalid_max_characters() -> None:
    with pytest.raises(
        ValueError,
        match="max_characters must be positive",
    ):
        DocumentChunkingConfig(max_characters=0)


def test_chunker_rejects_negative_overlap() -> None:
    with pytest.raises(
        ValueError,
        match="overlap_characters must not be negative",
    ):
        DocumentChunkingConfig(overlap_characters=-1)


def test_chunker_rejects_overlap_equal_to_maximum() -> None:
    with pytest.raises(
        ValueError,
        match="overlap_characters must be smaller than max_characters",
    ):
        DocumentChunkingConfig(
            max_characters=100,
            overlap_characters=100,
        )


def test_chunker_rejects_overlap_greater_than_maximum() -> None:
    with pytest.raises(
        ValueError,
        match="overlap_characters must be smaller than max_characters",
    ):
        DocumentChunkingConfig(
            max_characters=100,
            overlap_characters=150,
        )