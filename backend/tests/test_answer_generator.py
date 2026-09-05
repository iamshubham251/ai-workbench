"""Tests for the grounded answer generator contract."""

from uuid import uuid4

from app.models.document_chunk import DocumentChunk
from app.services.answer_generator import AnswerGenerator
from app.services.retriever import RetrievalResult


class StubAnswerGenerator:
    """Minimal implementation used to verify the provider contract."""

    def generate(
        self,
        query: str,
        results: tuple[RetrievalResult, ...],
    ) -> str:
        return f"Answer for: {query} using {len(results)} sources"


def test_answer_generator_protocol_accepts_implementation():
    """A concrete generator should satisfy the answer-generator contract."""
    generator: AnswerGenerator = StubAnswerGenerator()
    document_id = uuid4()

    results = (
        RetrievalResult(
            document_id=document_id,
            chunk_index=0,
            text="Safety inspection requires checking belt alignment.",
            score=0.95,
            page_numbers=(1,),
            section_title="Safety Requirements",
        ),
    )

    answer = generator.generate(
        "What does the inspection check?",
        results,
    )

    assert answer == "Answer for: What does the inspection check? using 1 sources"
