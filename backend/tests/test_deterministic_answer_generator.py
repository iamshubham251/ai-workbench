"""Tests for deterministic grounded answer generation."""

from uuid import uuid4

import pytest

from app.services.answer_generator import AnswerGenerationError
from app.services.deterministic_answer_generator import (
    DeterministicAnswerGenerator,
)
from app.services.retriever import RetrievalResult


def make_result(
    chunk_index: int,
    text: str,
    score: float = 0.9,
    page_numbers: tuple[int, ...] = (1,),
    section_title: str | None = "Safety Requirements",
) -> RetrievalResult:
    return RetrievalResult(
        document_id=uuid4(),
        chunk_index=chunk_index,
        text=text,
        score=score,
        page_numbers=page_numbers,
        section_title=section_title,
    )


def test_generator_returns_all_retrieved_evidence():
    generator = DeterministicAnswerGenerator()

    results = (
        make_result(
            0,
            "Check conveyor belt alignment.",
        ),
        make_result(
            1,
            "Verify emergency stops.",
            page_numbers=(2,),
        ),
    )

    answer = generator.generate(
        "What does the inspection check?",
        results,
    )

    assert 'What does the inspection check?' in answer
    assert "Check conveyor belt alignment." in answer
    assert "Verify emergency stops." in answer
    assert "chunk 0" in answer
    assert "chunk 1" in answer
    assert "page(s): 1" in answer
    assert "page(s): 2" in answer


def test_generator_preserves_retrieval_order():
    generator = DeterministicAnswerGenerator()

    results = (
        make_result(3, "Third evidence."),
        make_result(1, "First retrieved evidence."),
        make_result(2, "Second retrieved evidence."),
    )

    answer = generator.generate("test query", results)

    assert answer.index("Third evidence.") < answer.index(
        "First retrieved evidence."
    )
    assert answer.index("First retrieved evidence.") < answer.index(
        "Second retrieved evidence."
    )


def test_generator_rejects_empty_query():
    generator = DeterministicAnswerGenerator()

    with pytest.raises(ValueError, match="query must not be empty"):
        generator.generate("   ", (make_result(0, "Evidence."),))


def test_generator_rejects_empty_evidence():
    generator = DeterministicAnswerGenerator()

    with pytest.raises(
        AnswerGenerationError,
        match="No supporting evidence",
    ):
        generator.generate("What is required?", ())


def test_generator_handles_missing_page_and_section_metadata():
    generator = DeterministicAnswerGenerator()

    result = make_result(
        0,
        "General inspection requirement.",
        page_numbers=(),
        section_title=None,
    )

    answer = generator.generate("What is required?", (result,))

    assert "page(s): unknown" in answer
    assert "section:" not in answer
