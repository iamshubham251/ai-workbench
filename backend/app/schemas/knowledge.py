from uuid import UUID

from pydantic import BaseModel


class KnowledgeIngestionResponse(BaseModel):
    """Public response for a document added to the knowledge base."""

    document_id: UUID
    chunk_count: int
    embedding_count: int
