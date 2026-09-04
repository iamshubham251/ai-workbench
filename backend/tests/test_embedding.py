"""Tests for embedding domain types and provider contract."""

from uuid import uuid4

import pytest

from app.models.document_chunk import DocumentChunk
from app.models.embedding import DocumentEmbedding
from app.services.embedding_provider import EmbeddingError


def create_chunk() -> DocumentChunk:
    """Create a sample document chunk."""
    return DocumentChunk(
        document_id=uuid4(),
        chunk_index=0,
        text="Sample document content.",
        page_numbers=(1,),
    )


def test_embedding_stores_document_id() -> None:
    document_id = uuid4()

    embedding = DocumentEmbedding(
        document_id=document_id,
        chunk_index=0,
        vector=(0.1, 0.2, 0.3),
    )

    assert embedding.document_id == document_id


def test_embedding_stores_chunk_index() -> None:
    embedding = DocumentEmbedding(
        document_id=uuid4(),
        chunk_index=3,
        vector=(0.1, 0.2),
    )

    assert embedding.chunk_index == 3


def test_embedding_stores_vector() -> None:
    vector = (0.1, 0.2, 0.3)

    embedding = DocumentEmbedding(
        document_id=uuid4(),
        chunk_index=0,
        vector=vector,
    )

    assert embedding.vector == vector


def test_embedding_reports_dimensions() -> None:
    embedding = DocumentEmbedding(
        document_id=uuid4(),
        chunk_index=0,
        vector=(0.1, 0.2, 0.3, 0.4),
    )

    assert embedding.dimensions == 4


def test_embedding_accepts_integer_values() -> None:
    embedding = DocumentEmbedding(
        document_id=uuid4(),
        chunk_index=0,
        vector=(1, 2, 3),
    )

    assert embedding.vector == (1, 2, 3)


def test_embedding_rejects_negative_chunk_index() -> None:
    with pytest.raises(
        ValueError,
        match="chunk_index must not be negative",
    ):
        DocumentEmbedding(
            document_id=uuid4(),
            chunk_index=-1,
            vector=(0.1, 0.2),
        )


def test_embedding_rejects_empty_vector() -> None:
    with pytest.raises(
        ValueError,
        match="vector must not be empty",
    ):
        DocumentEmbedding(
            document_id=uuid4(),
            chunk_index=0,
            vector=(),
        )


def test_embedding_rejects_non_numeric_vector_values() -> None:
    with pytest.raises(
        ValueError,
        match="vector values must be numeric",
    ):
        DocumentEmbedding(
            document_id=uuid4(),
            chunk_index=0,
            vector=(0.1, "invalid"),  # type: ignore[arg-type]
        )


def test_embedding_error_is_runtime_error() -> None:
    error = EmbeddingError("embedding failed")

    assert isinstance(error, RuntimeError)


def test_sample_chunk_is_compatible_with_embedding_identity() -> None:
    chunk = create_chunk()

    embedding = DocumentEmbedding(
        document_id=chunk.document_id,
        chunk_index=chunk.chunk_index,
        vector=(0.1, 0.2, 0.3),
    )

    assert embedding.document_id == chunk.document_id
    assert embedding.chunk_index == chunk.chunk_index
