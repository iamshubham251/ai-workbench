"""Deterministic grounded answer generation from retrieved evidence."""

from app.services.answer_generator import (
    AnswerGenerationError,
    AnswerGenerator,
)
from app.services.retriever import RetrievalResult


class DeterministicAnswerGenerator:
    """Build a grounded answer directly from retrieved evidence.

    This implementation intentionally performs no inference or fact generation.
    It provides a deterministic baseline until a model-backed generator is added.
    """

    def generate(
        self,
        query: str,
        results: tuple[RetrievalResult, ...],
    ) -> str:
        if not query.strip():
            raise ValueError("query must not be empty")

        if not results:
            raise AnswerGenerationError(
                "No supporting evidence was retrieved for the query"
            )

        evidence_lines: list[str] = []

        for result in results:
            source = self._format_source(result)
            evidence_lines.append(
                f"- {result.text.strip()} [{source}]"
            )

        return (
            f"Based on the retrieved knowledge-base evidence for "
            f"the query \"{query.strip()}\":\n"
            + "\n".join(evidence_lines)
        )

    @staticmethod
    def _format_source(result: RetrievalResult) -> str:
        page_text = (
            ", ".join(str(page) for page in result.page_numbers)
            if result.page_numbers
            else "unknown"
        )

        section_text = (
            f", section: {result.section_title.strip()}"
            if result.section_title
            else ""
        )

        return (
            f"document {result.document_id}, "
            f"chunk {result.chunk_index}, "
            f"page(s): {page_text}"
            f"{section_text}"
        )
