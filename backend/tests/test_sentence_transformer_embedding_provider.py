"""Tests for the Sentence Transformers embedding provider."""

from uuid import uuid4

import pytest

from app.models.document_chunk import DocumentChunk
from app.models.embedding import DocumentEmbedding
from app.services.embedding_provider import EmbeddingError
from app.services.sentence_transformer_embedding_provider import (
    SentenceTransformerEmbeddingProvider,
)


MODEL_NAME = "all-MiniLM-L6-v2"


def create_chunk(
    chunk_index: int = 0,
    text: str = "AI Workbench inspection finding.",
) -> DocumentChunk:
    """Create a sample document chunk."""
    return DocumentChunk(
        document_id=uuid4(),
        chunk_index=chunk_index,
        text=text,
        page_numbers=(1,),
    )


@pytest.fixture(scope="module")
def provider() -> SentenceTransformerEmbeddingProvider:
    """Load the real local embedding model once for this test module."""
    return SentenceTransformerEmbeddingProvider(
        model_name=MODEL_NAME,
    )


def test_provider_loads_model(
    provider: SentenceTransformerEmbeddingProvider,
) -> None:
    assert provider.model_name == MODEL_NAME
    assert provider.model is not None


def test_provider_generates_embedding(
    provider: SentenceTransformerEmbeddingProvider,
) -> None:
    chunk = create_chunk()

    embedding = provider.embed(chunk)

    assert isinstance(embedding, DocumentEmbedding)
    assert embedding.document_id == chunk.document_id
    assert embedding.chunk_index == chunk.chunk_index
    assert embedding.dimensions == 384


def test_provider_generates_normalized_embedding(
    provider: SentenceTransformerEmbeddingProvider,
) -> None:
    chunk = create_chunk()

    embedding = provider.embed(chunk)

    magnitude = sum(
        value * value
        for value in embedding.vector
    ) ** 0.5

    assert magnitude == pytest.approx(1.0, abs=1e-5)


def test_provider_generates_deterministic_embedding(
    provider: SentenceTransformerEmbeddingProvider,
) -> None:
    chunk = create_chunk()

    first = provider.embed(chunk)
    second = provider.embed(chunk)

    assert first.vector == pytest.approx(
        second.vector,
        abs=1e-6,
    )


def test_provider_generates_batch_embeddings(
    provider: SentenceTransformerEmbeddingProvider,
) -> None:
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Inspection finding one.",
            page_numbers=(1,),
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=1,
            text="Inspection finding two.",
            page_numbers=(2,),
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=2,
            text="Inspection finding three.",
            page_numbers=(3,),
        ),
    )

    embeddings = provider.embed_batch(chunks)

    assert len(embeddings) == 3
    assert all(
        isinstance(embedding, DocumentEmbedding)
        for embedding in embeddings
    )
    assert [embedding.chunk_index for embedding in embeddings] == [
        0,
        1,
        2,
    ]
    assert all(
        embedding.dimensions == 384
        for embedding in embeddings
    )


def test_provider_preserves_document_identity_in_batch(
    provider: SentenceTransformerEmbeddingProvider,
) -> None:
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="First chunk.",
            page_numbers=(1,),
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=1,
            text="Second chunk.",
            page_numbers=(2,),
        ),
    )

    embeddings = provider.embed_batch(chunks)

    assert all(
        embedding.document_id == document_id
        for embedding in embeddings
    )


def test_provider_returns_empty_batch_for_empty_input(
    provider: SentenceTransformerEmbeddingProvider,
) -> None:
    assert provider.embed_batch(()) == ()


def test_provider_rejects_empty_model_name() -> None:
    with pytest.raises(
        ValueError,
        match="model_name must not be empty",
    ):
        SentenceTransformerEmbeddingProvider(
            model_name="   ",
        )


def test_provider_raises_embedding_error_for_missing_model() -> None:
    with pytest.raises(
        EmbeddingError,
        match="Embedding model could not be loaded",
    ):
        SentenceTransformerEmbeddingProvider(
            model_name="this-model-does-not-exist-anywhere",
        )
