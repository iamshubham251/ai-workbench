import sqlite3
from uuid import uuid4

from app.models.embedding import DocumentEmbedding
from app.repositories.embedding_repository import EmbeddingRepository


def test_save_and_get_embeddings():
    connection = sqlite3.connect(":memory:")
    repository = EmbeddingRepository(connection)

    document_id = uuid4()

    embeddings = (
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=0,
            vector=(0.1, 0.2, 0.3),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=1,
            vector=(0.4, 0.5, 0.6),
        ),
    )

    repository.save(document_id, embeddings)

    result = repository.get_by_document_id(document_id)

    assert result == embeddings


def test_embeddings_are_returned_in_chunk_order():
    connection = sqlite3.connect(":memory:")
    repository = EmbeddingRepository(connection)

    document_id = uuid4()

    embeddings = (
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=2,
            vector=(0.3, 0.4),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=0,
            vector=(0.1, 0.2),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=1,
            vector=(0.2, 0.3),
        ),
    )

    repository.save(document_id, embeddings)

    result = repository.get_by_document_id(document_id)

    assert [embedding.chunk_index for embedding in result] == [0, 1, 2]


def test_count_embeddings():
    connection = sqlite3.connect(":memory:")
    repository = EmbeddingRepository(connection)

    document_id = uuid4()

    embeddings = (
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=0,
            vector=(0.1, 0.2),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=1,
            vector=(0.3, 0.4),
        ),
    )

    repository.save(document_id, embeddings)

    assert repository.count_by_document_id(document_id) == 2


def test_save_replaces_existing_embeddings():
    connection = sqlite3.connect(":memory:")
    repository = EmbeddingRepository(connection)

    document_id = uuid4()

    repository.save(
        document_id,
        (
            DocumentEmbedding(
                document_id=document_id,
                chunk_index=0,
                vector=(0.1, 0.2),
            ),
        ),
    )

    repository.save(
        document_id,
        (
            DocumentEmbedding(
                document_id=document_id,
                chunk_index=0,
                vector=(0.9, 0.8),
            ),
            DocumentEmbedding(
                document_id=document_id,
                chunk_index=1,
                vector=(0.7, 0.6),
            ),
        ),
    )

    result = repository.get_by_document_id(document_id)

    assert result == (
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=0,
            vector=(0.9, 0.8),
        ),
        DocumentEmbedding(
            document_id=document_id,
            chunk_index=1,
            vector=(0.7, 0.6),
        ),
    )

    assert repository.count_by_document_id(document_id) == 2


def test_delete_embeddings():
    connection = sqlite3.connect(":memory:")
    repository = EmbeddingRepository(connection)

    document_id = uuid4()

    repository.save(
        document_id,
        (
            DocumentEmbedding(
                document_id=document_id,
                chunk_index=0,
                vector=(0.1, 0.2),
            ),
        ),
    )

    repository.delete_by_document_id(document_id)

    assert repository.get_by_document_id(document_id) == ()
    assert repository.count_by_document_id(document_id) == 0


def test_documents_are_isolated():
    connection = sqlite3.connect(":memory:")
    repository = EmbeddingRepository(connection)

    document_a = uuid4()
    document_b = uuid4()

    repository.save(
        document_a,
        (
            DocumentEmbedding(
                document_id=document_a,
                chunk_index=0,
                vector=(0.1, 0.2),
            ),
        ),
    )

    repository.save(
        document_b,
        (
            DocumentEmbedding(
                document_id=document_b,
                chunk_index=0,
                vector=(0.9, 0.8),
            ),
        ),
    )

    assert repository.count_by_document_id(document_a) == 1
    assert repository.count_by_document_id(document_b) == 1

    assert repository.get_by_document_id(document_a)[0].vector == (0.1, 0.2)
    assert repository.get_by_document_id(document_b)[0].vector == (0.9, 0.8)

def test_repository_returns_embeddings_across_documents_in_stable_order():
    document_a = uuid4()
    document_b = uuid4()

    embeddings_a = (
        DocumentEmbedding(
            document_id=document_a,
            chunk_index=1,
            vector=(0.2, 0.3),
        ),
        DocumentEmbedding(
            document_id=document_a,
            chunk_index=0,
            vector=(0.1, 0.2),
        ),
    )

    embeddings_b = (
        DocumentEmbedding(
            document_id=document_b,
            chunk_index=0,
            vector=(0.9, 0.8),
        ),
    )

    connection = sqlite3.connect(":memory:")
    repository = EmbeddingRepository(connection)

    repository.save(document_a, embeddings_a)
    repository.save(document_b, embeddings_b)

    results = repository.get_all()

    expected = sorted(
        (
            (document_a, 0, (0.1, 0.2)),
            (document_a, 1, (0.2, 0.3)),
            (document_b, 0, (0.9, 0.8)),
        ),
        key=lambda item: (str(item[0]), item[1]),
    )

    assert [
        (embedding.document_id, embedding.chunk_index, embedding.vector)
        for embedding in results
    ] == expected
