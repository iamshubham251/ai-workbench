"""Knowledge base ingestion routes."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import (
    get_document_service,
    get_knowledge_ingestion_service,
)
from app.schemas.knowledge import KnowledgeIngestionResponse
from app.services.document_service import DocumentService
from app.services.knowledge_ingestion_service import KnowledgeIngestionService


router = APIRouter()


@router.post(
    "/{document_id}/ingest",
    response_model=KnowledgeIngestionResponse,
)
def ingest_document(
    document_id: UUID,
    document_service: DocumentService = Depends(get_document_service),
    ingestion_service: KnowledgeIngestionService = Depends(
        get_knowledge_ingestion_service
    ),
) -> KnowledgeIngestionResponse:
    document = document_service.get_document(document_id)
    result = ingestion_service.ingest(document)

    return KnowledgeIngestionResponse(
        document_id=result.document_id,
        chunk_count=result.chunk_count,
        embedding_count=result.embedding_count,
    )


@router.get(
    "/{document_id}/status",
    response_model=KnowledgeIngestionResponse,
)
def get_ingestion_status(
    document_id: UUID,
    document_service: DocumentService = Depends(get_document_service),
    ingestion_service: KnowledgeIngestionService = Depends(
        get_knowledge_ingestion_service
    ),
) -> KnowledgeIngestionResponse:
    document_service.get_document(document_id)

    result = ingestion_service.get_status(document_id)

    return KnowledgeIngestionResponse(
        document_id=result.document_id,
        chunk_count=result.chunk_count,
        embedding_count=result.embedding_count,
    )
