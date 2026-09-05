from uuid import uuid4

import pytest

from app.models.document_chunk import DocumentChunk
from app.models.embedding import DocumentEmbedding
from app.services.retriever import Retriever


def test_retriever_returns_results_in_similarity_order():
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Conveyor belt inspection procedure.",
            page_numbers=(1,),
            section_title="Inspection",
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=1,
            text="Employee attendance procedure.",
            page_numbers=(2,),
            section_title="HR",
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=2,
            text="Conveyor belt emergency shutdown procedure.",
            page_numbers=(3,),
            section_title="Safety",
        ),
    )

    embeddings = (
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=0,
            vector=(0.8, 0.2),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=1,
            vector=(0.1, 0.9),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=2,
            vector=(0.95, 0.05),
        ),
    )

    results = Retriever().retrieve(
        query_embedding=(1.0, 0.0),
        chunks=chunks,
        embeddings=embeddings,
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].chunk_index == 2
    assert results[1].chunk_index == 0
    assert results[0].score > results[1].score


def test_retriever_respects_top_k():
    document_id = uuid4()

    chunks = tuple(
        DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            text=f"Chunk {index}",
        )
        for index in range(5)
    )

    embeddings = tuple(
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=index,
            vector=(float(index + 1), 0.0),
        )
        for index in range(5)
    )

    results = Retriever().retrieve(
        query_embedding=(1.0, 0.0),
        chunks=chunks,
        embeddings=embeddings,
        top_k=3,
    )

    assert len(results) == 3


def test_retriever_skips_embeddings_without_chunks():
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Known chunk",
        ),
    )

    embeddings = (
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=0,
            vector=(1.0, 0.0),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=99,
            vector=(0.9, 0.1),
        ),
    )

    results = Retriever().retrieve(
        query_embedding=(1.0, 0.0),
        chunks=chunks,
        embeddings=embeddings,
    )

    assert len(results) == 1
    assert results[0].chunk_index == 0


def test_retriever_rejects_invalid_top_k():
    with pytest.raises(ValueError, match="top_k"):
        Retriever().retrieve(
            query_embedding=(1.0, 0.0),
            chunks=(),
            embeddings=(),
            top_k=0,
        )


def test_retriever_preserves_chunk_metadata():
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Safety inspection requirement.",
            page_numbers=(4, 5),
            section_title="Safety Requirements",
        ),
    )

    embeddings = (
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=0,
            vector=(1.0, 0.0),
        ),
    )

    result = Retriever().retrieve(
        query_embedding=(1.0, 0.0),
        chunks=chunks,
        embeddings=embeddings,
        top_k=1,
    )[0]

    assert result.document_id == document_id
    assert result.chunk_index == 0
    assert result.text == "Safety inspection requirement."
    assert result.page_numbers == (4, 5)
    assert result.section_title == "Safety Requirements"
    assert result.score == pytest.approx(1.0)

def test_retriever_uses_chunk_index_as_deterministic_tiebreaker():
    """Equal similarity scores must produce stable chunk ordering."""
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=2,
            text="Second chunk",
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="First chunk",
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=1,
            text="Middle chunk",
        ),
    )

    embeddings = (
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=2,
            vector=(1.0, 0.0),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=0,
            vector=(1.0, 0.0),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=1,
            vector=(1.0, 0.0),
        ),
    )

    results = Retriever().retrieve(
        query_embedding=(1.0, 0.0),
        chunks=chunks,
        embeddings=embeddings,
        top_k=3,
    )

    assert [result.chunk_index for result in results] == [0, 1, 2]

def test_retriever_filters_results_below_minimum_score():
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Highly relevant chunk",
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=1,
            text="Weakly relevant chunk",
        ),
    )

    embeddings = (
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=0,
            vector=(1.0, 0.0),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=1,
            vector=(0.6, 0.8),
        ),
    )

    results = Retriever().retrieve(
        query_embedding=(1.0, 0.0),
        chunks=chunks,
        embeddings=embeddings,
        top_k=5,
        min_score=0.9,
    )

    assert len(results) == 1
    assert results[0].chunk_index == 0
    assert results[0].score >= 0.9


def test_retriever_rejects_invalid_min_score():
    document_id = uuid4()

    with pytest.raises(ValueError, match="min_score"):
        Retriever().retrieve(
            query_embedding=(1.0, 0.0),
            chunks=(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=0,
                    text="Test chunk",
                ),
            ),
            embeddings=(
                DocumentEmbedding(
                    document_id=document_id,
                    chunk_index=0,
                    vector=(1.0, 0.0),
                ),
            ),
            min_score=1.1,
        )

def test_retriever_matches_chunks_by_document_and_chunk_index():
    """Chunks must be matched using the composite (document_id, chunk_index) key."""
    document_a = uuid4()
    document_b = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_a,
            chunk_index=0,
            text="Document A chunk zero",
        ),
        DocumentChunk(
            document_id=document_b,
            chunk_index=0,
            text="Document B chunk zero",
        ),
    )

    embeddings = (
        DocumentEmbedding(
            document_id=document_a,
            chunk_index=0,
            vector=(1.0, 0.0),
        ),
        DocumentEmbedding(
            document_id=document_b,
            chunk_index=0,
            vector=(0.0, 1.0),
        ),
    )

    results = Retriever().retrieve(
        query_embedding=(1.0, 0.0),
        chunks=chunks,
        embeddings=embeddings,
        top_k=5,
    )

    assert len(results) == 2
    assert results[0].document_id == document_a
    assert results[0].chunk_index == 0
    assert results[0].text == "Document A chunk zero"
    assert results[0].score == pytest.approx(1.0)

    assert results[1].document_id == document_b
    assert results[1].chunk_index == 0
    assert results[1].text == "Document B chunk zero"
    assert results[1].score == pytest.approx(0.0)
