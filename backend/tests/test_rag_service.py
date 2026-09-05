import sqlite3
from uuid import uuid4

import pytest

from app.models.document_chunk import DocumentChunk
from app.repositories.chunk_sql_repository import SqlChunkRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.deterministic_answer_generator import (
    DeterministicAnswerGenerator,
)
from app.services.query_embedding_service import QueryEmbeddingService
from app.services.rag_service import RagService


def build_rag_service(connection: sqlite3.Connection) -> RagService:
    """Build a RAG service with the deterministic generator."""
    return RagService(
        chunk_repository=SqlChunkRepository(connection),
        embedding_repository=EmbeddingRepository(connection),
        query_embedding_service=QueryEmbeddingService(),
        answer_generator=DeterministicAnswerGenerator(),
    )


def test_rag_service_retrieves_relevant_chunk():
    connection = sqlite3.connect(":memory:")

    chunk_repository = SqlChunkRepository(connection)
    embedding_repository = EmbeddingRepository(connection)

    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text=(
                "Conveyor belt inspection must be performed "
                "before starting daily operations."
            ),
            page_numbers=(1,),
            section_title="Inspection Procedure",
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=1,
            text=(
                "Employees must submit attendance records "
                "before the end of each working day."
            ),
            page_numbers=(2,),
            section_title="Attendance",
        ),
    )

    chunk_repository.save(document_id, chunks)

    query_service = QueryEmbeddingService()
    chunk_embeddings = query_service.provider.embed_batch(chunks)

    embedding_repository.save(
        document_id,
        chunk_embeddings,
    )

    rag_service = RagService(
        chunk_repository=chunk_repository,
        embedding_repository=embedding_repository,
        query_embedding_service=query_service,
        answer_generator=DeterministicAnswerGenerator(),
    )

    response = rag_service.query(
        document_id=document_id,
        query="What is the conveyor belt inspection procedure?",
        top_k=1,
    )

    assert response.query == (
        "What is the conveyor belt inspection procedure?"
    )
    assert response.result_count == 1
    assert response.answer
    assert "Conveyor belt inspection" in response.answer
    assert "Inspection Procedure" in response.answer
    assert "page(s): 1" in response.answer

    result = response.results[0]

    assert result.chunk_index == 0
    assert "Conveyor belt inspection" in result.text
    assert result.section_title == "Inspection Procedure"
    assert result.page_numbers == (1,)
    assert result.score > 0.5


def test_rag_service_returns_empty_for_unknown_document():
    connection = sqlite3.connect(":memory:")

    rag_service = build_rag_service(connection)

    response = rag_service.query(
        document_id=uuid4(),
        query="What is the inspection procedure?",
    )

    assert response.result_count == 0
    assert response.answer == (
        "No supporting evidence was found for this query."
    )


def test_rag_service_rejects_empty_query():
    connection = sqlite3.connect(":memory:")

    rag_service = build_rag_service(connection)

    with pytest.raises(ValueError, match="query must not be empty"):
        rag_service.query(
            document_id=uuid4(),
            query="   ",
        )
