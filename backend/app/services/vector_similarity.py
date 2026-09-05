"""Vector similarity utilities for local RAG retrieval."""

import math


class SimilarityError(ValueError):
    """Raised when vectors cannot be compared."""


def cosine_similarity(
    vector_a: tuple[float, ...],
    vector_b: tuple[float, ...],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if not vector_a or not vector_b:
        raise SimilarityError("vectors must not be empty")

    if len(vector_a) != len(vector_b):
        raise SimilarityError("vectors must have the same dimensions")

    norm_a = math.sqrt(sum(value * value for value in vector_a))
    norm_b = math.sqrt(sum(value * value for value in vector_b))

    if norm_a == 0.0 or norm_b == 0.0:
        raise SimilarityError("zero vectors are not supported")

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )

    return dot_product / (norm_a * norm_b)
