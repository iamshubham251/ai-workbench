"""Build grounded context for agent tasks."""

from app.models.agent_context import AgentContext, AgentContextItem
from app.services.rag_service import RagService


class AgentContextBuilder:
    """Retrieve and normalize relevant knowledge for an agent task."""

    def __init__(self, rag_service: RagService) -> None:
        self._rag_service = rag_service

    def build(
        self,
        instruction: str,
        document_ids: tuple = (),
        top_k: int = 5,
    ) -> AgentContext:
        """Build context from the requested documents or the global knowledge base."""

        if not instruction.strip():
            raise ValueError("instruction must not be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        if document_ids:
            results = []
            for document_id in document_ids:
                response = self._rag_service.query(
                    document_id=document_id,
                    query=instruction,
                    top_k=top_k,
                )
                results.extend(response.results)
        else:
            response = self._rag_service.query_all(
                query=instruction,
                top_k=top_k,
            )
            results = list(response.results)

        return AgentContext(
            items=tuple(
                AgentContextItem(
                    document_id=result.document_id,
                    chunk_index=result.chunk_index,
                    text=result.text,
                    score=result.score,
                    page_numbers=result.page_numbers,
                    section_title=result.section_title,
                )
                for result in results
            )
        )
