import pytest

from app.services.vector_similarity import (
    SimilarityError,
    cosine_similarity,
)


def test_identical_vectors_have_similarity_one():
    assert cosine_similarity(
        (1.0, 2.0, 3.0),
        (1.0, 2.0, 3.0),
    ) == pytest.approx(1.0)


def test_orthogonal_vectors_have_similarity_zero():
    assert cosine_similarity(
        (1.0, 0.0),
        (0.0, 1.0),
    ) == pytest.approx(0.0)


def test_opposite_vectors_have_similarity_negative_one():
    assert cosine_similarity(
        (1.0, 0.0),
        (-1.0, 0.0),
    ) == pytest.approx(-1.0)


def test_scaled_vectors_have_similarity_one():
    assert cosine_similarity(
        (1.0, 2.0),
        (2.0, 4.0),
    ) == pytest.approx(1.0)


def test_empty_vectors_raise_error():
    with pytest.raises(SimilarityError, match="must not be empty"):
        cosine_similarity((), (1.0,))


def test_different_dimensions_raise_error():
    with pytest.raises(
        SimilarityError,
        match="same dimensions",
    ):
        cosine_similarity(
            (1.0, 2.0),
            (1.0, 2.0, 3.0),
        )


def test_zero_vector_raises_error():
    with pytest.raises(
        SimilarityError,
        match="zero vectors",
    ):
        cosine_similarity(
            (0.0, 0.0),
            (1.0, 2.0),
        )
