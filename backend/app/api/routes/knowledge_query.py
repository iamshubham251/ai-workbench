"""Knowledge base query routes."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import get_document_service, get_rag_service
from app.schemas.knowledge_query import (
    KnowledgeQueryRequest,
    KnowledgeQueryResponse,
    KnowledgeQueryResult,
)
from app.services.document_service import DocumentService
from app.services.rag_service import RagService


router = APIRouter()


@router.post(
    "/{document_id}/query",
    response_model=KnowledgeQueryResponse,
)
def query_knowledge(
    document_id: UUID,
    request: KnowledgeQueryRequest,
    document_service: DocumentService = Depends(get_document_service),
    rag_service: RagService = Depends(get_rag_service),
) -> KnowledgeQueryResponse:
    document_service.get_document(document_id)

    result = rag_service.query(
        document_id=document_id,
        query=request.query,
        top_k=request.top_k,
    )

    return KnowledgeQueryResponse(
        query=result.query,
        answer=result.answer,
        result_count=result.result_count,
        results=tuple(
            KnowledgeQueryResult(
                document_id=item.document_id,
                chunk_index=item.chunk_index,
                text=item.text,
                score=item.score,
                page_numbers=item.page_numbers,
                section_title=item.section_title,
            )
            for item in result.results
        ),
    )
