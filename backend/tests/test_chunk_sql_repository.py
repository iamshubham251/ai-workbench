"""Tests for the SQLite document chunk repository."""

import sqlite3
from uuid import uuid4

from app.models.document_chunk import DocumentChunk
from app.repositories.chunk_sql_repository import SqlChunkRepository


def create_chunks(
    document_id,
) -> tuple[DocumentChunk, ...]:
    """Create sample chunks for repository tests."""
    return (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="First document chunk.",
            page_numbers=(1,),
            section_title="INTRODUCTION",
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=1,
            text="Second document chunk.",
            page_numbers=(1, 2),
            section_title="FINDINGS",
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=2,
            text="Third document chunk.",
            page_numbers=(3,),
        ),
    )


def create_repository() -> tuple[sqlite3.Connection, SqlChunkRepository]:
    """Create an isolated in-memory SQLite repository."""
    connection = sqlite3.connect(":memory:")
    repository = SqlChunkRepository(connection)

    return connection, repository


def test_repository_stores_and_retrieves_chunks() -> None:
    document_id = uuid4()
    chunks = create_chunks(document_id)

    connection, repository = create_repository()

    repository.save(document_id, chunks)

    assert repository.get_by_document_id(document_id) == chunks

    connection.close()


def test_repository_preserves_chunk_order() -> None:
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=2,
            text="Third chunk.",
            page_numbers=(3,),
        ),
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

    connection, repository = create_repository()

    repository.save(document_id, chunks)

    retrieved = repository.get_by_document_id(document_id)

    assert [chunk.chunk_index for chunk in retrieved] == [0, 1, 2]

    connection.close()


def test_repository_preserves_page_numbers() -> None:
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Chunk spanning pages.",
            page_numbers=(2, 3, 4),
        ),
    )

    connection, repository = create_repository()

    repository.save(document_id, chunks)

    retrieved = repository.get_by_document_id(document_id)

    assert retrieved[0].page_numbers == (2, 3, 4)

    connection.close()


def test_repository_preserves_section_title() -> None:
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Inspection finding.",
            page_numbers=(1,),
            section_title="INSPECTION FINDINGS",
        ),
    )

    connection, repository = create_repository()

    repository.save(document_id, chunks)

    retrieved = repository.get_by_document_id(document_id)

    assert retrieved[0].section_title == "INSPECTION FINDINGS"

    connection.close()


def test_repository_handles_missing_section_title() -> None:
    document_id = uuid4()

    chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Unclassified content.",
            page_numbers=(1,),
        ),
    )

    connection, repository = create_repository()

    repository.save(document_id, chunks)

    retrieved = repository.get_by_document_id(document_id)

    assert retrieved[0].section_title is None

    connection.close()


def test_repository_counts_chunks() -> None:
    document_id = uuid4()
    chunks = create_chunks(document_id)

    connection, repository = create_repository()

    repository.save(document_id, chunks)

    assert repository.count_by_document_id(document_id) == 3

    connection.close()


def test_repository_returns_empty_for_unknown_document() -> None:
    connection, repository = create_repository()

    assert repository.get_by_document_id(uuid4()) == ()
    assert repository.count_by_document_id(uuid4()) == 0

    connection.close()


def test_repository_replaces_existing_chunks() -> None:
    document_id = uuid4()
    first_chunks = create_chunks(document_id)

    replacement_chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Replacement chunk.",
            page_numbers=(5,),
        ),
    )

    connection, repository = create_repository()

    repository.save(document_id, first_chunks)
    repository.save(document_id, replacement_chunks)

    assert repository.get_by_document_id(document_id) == replacement_chunks
    assert repository.count_by_document_id(document_id) == 1

    connection.close()


def test_repository_deletes_chunks() -> None:
    document_id = uuid4()
    chunks = create_chunks(document_id)

    connection, repository = create_repository()

    repository.save(document_id, chunks)
    repository.delete_by_document_id(document_id)

    assert repository.get_by_document_id(document_id) == ()
    assert repository.count_by_document_id(document_id) == 0

    connection.close()


def test_repository_persists_across_connections() -> None:
    document_id = uuid4()
    chunks = create_chunks(document_id)

    database = "file:chunk_test?mode=memory&cache=shared"

    connection_one = sqlite3.connect(
        database,
        uri=True,
    )
    connection_two = sqlite3.connect(
        database,
        uri=True,
    )

    repository_one = SqlChunkRepository(connection_one)
    repository_two = SqlChunkRepository(connection_two)

    repository_one.save(document_id, chunks)

    assert repository_two.get_by_document_id(document_id) == chunks

    connection_one.close()
    connection_two.close()


def test_repository_delete_unknown_document_is_safe() -> None:
    connection, repository = create_repository()

    repository.delete_by_document_id(uuid4())

    connection.close()

def test_repository_returns_chunks_across_documents_in_stable_order() -> None:
    document_a = uuid4()
    document_b = uuid4()

    chunks_a = (
        DocumentChunk(
            document_id=document_a,
            chunk_index=1,
            text="Document A second chunk.",
        ),
        DocumentChunk(
            document_id=document_a,
            chunk_index=0,
            text="Document A first chunk.",
        ),
    )

    chunks_b = (
        DocumentChunk(
            document_id=document_b,
            chunk_index=0,
            text="Document B first chunk.",
        ),
    )

    connection, repository = create_repository()

    repository.save(document_a, chunks_a)
    repository.save(document_b, chunks_b)

    results = repository.get_all()

    expected_documents = sorted(
        (
            (document_a, 0, "Document A first chunk."),
            (document_a, 1, "Document A second chunk."),
            (document_b, 0, "Document B first chunk."),
        ),
        key=lambda item: (str(item[0]), item[1]),
    )

    assert [
        (chunk.document_id, chunk.chunk_index, chunk.text)
        for chunk in results
    ] == expected_documents

    connection.close()

