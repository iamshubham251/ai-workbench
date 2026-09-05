"""Interface for grounded RAG answer generation."""

from typing import Protocol

from app.services.retriever import RetrievalResult


class AnswerGenerationError(RuntimeError):
    """Raised when grounded answer generation fails."""


class AnswerGenerator(Protocol):
    """Generate an answer using only retrieved evidence."""

    def generate(
        self,
        query: str,
        results: tuple[RetrievalResult, ...],
    ) -> str:
        """Generate a grounded answer from retrieved results."""
        ...
