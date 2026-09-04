"""Tests for the document chunk repository."""

from uuid import uuid4

from app.models.document_chunk import DocumentChunk
from app.repositories.chunk_repository import ChunkRepository


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
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=1,
            text="Second document chunk.",
            page_numbers=(1,),
        ),
    )


def test_repository_stores_and_retrieves_chunks() -> None:
    document_id = uuid4()
    chunks = create_chunks(document_id)

    repository = ChunkRepository()

    repository.save(document_id, chunks)

    assert repository.get_by_document_id(document_id) == chunks


def test_repository_returns_empty_tuple_for_unknown_document() -> None:
    repository = ChunkRepository()

    assert repository.get_by_document_id(uuid4()) == ()


def test_repository_counts_chunks() -> None:
    document_id = uuid4()
    chunks = create_chunks(document_id)

    repository = ChunkRepository()
    repository.save(document_id, chunks)

    assert repository.count_by_document_id(document_id) == 2


def test_repository_count_is_zero_for_unknown_document() -> None:
    repository = ChunkRepository()

    assert repository.count_by_document_id(uuid4()) == 0


def test_repository_replaces_existing_chunks() -> None:
    document_id = uuid4()
    first_chunks = create_chunks(document_id)

    second_chunks = (
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            text="Replacement chunk.",
            page_numbers=(2,),
        ),
    )

    repository = ChunkRepository()

    repository.save(document_id, first_chunks)
    repository.save(document_id, second_chunks)

    assert repository.get_by_document_id(document_id) == second_chunks
    assert repository.count_by_document_id(document_id) == 1


def test_repository_deletes_chunks() -> None:
    document_id = uuid4()
    chunks = create_chunks(document_id)

    repository = ChunkRepository()
    repository.save(document_id, chunks)

    repository.delete_by_document_id(document_id)

    assert repository.get_by_document_id(document_id) == ()
    assert repository.count_by_document_id(document_id) == 0


def test_repository_delete_unknown_document_is_safe() -> None:
    repository = ChunkRepository()

    repository.delete_by_document_id(uuid4())