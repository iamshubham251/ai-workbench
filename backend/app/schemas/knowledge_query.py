from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgeQueryRequest(BaseModel):
    """Request body for semantic knowledge-base search."""

    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class KnowledgeQueryResult(BaseModel):
    """A retrieved knowledge-base chunk."""

    document_id: UUID
    chunk_index: int
    text: str
    score: float
    page_numbers: tuple[int, ...]
    section_title: str | None


class KnowledgeQueryResponse(BaseModel):
    """Semantic search response with a grounded answer."""

    query: str
    answer: str
    result_count: int
    results: tuple[KnowledgeQueryResult, ...]
