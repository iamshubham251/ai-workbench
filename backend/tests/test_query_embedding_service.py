import pytest

from app.services.query_embedding_service import QueryEmbeddingService


@pytest.fixture(scope="module")
def service():
    return QueryEmbeddingService()


def test_query_embedding_is_generated(service):
    vector = service.embed_query(
        "What is the required conveyor belt inspection procedure?"
    )

    assert vector
    assert len(vector) == 384


def test_query_embedding_is_normalized(service):
    vector = service.embed_query(
        "What are the safety requirements?"
    )

    magnitude = sum(value * value for value in vector) ** 0.5

    assert magnitude == pytest.approx(1.0, abs=1e-5)


def test_empty_query_is_rejected(service):
    with pytest.raises(ValueError, match="query must not be empty"):
        service.embed_query("")


def test_whitespace_query_is_rejected(service):
    with pytest.raises(ValueError, match="query must not be empty"):
        service.embed_query("   ")
