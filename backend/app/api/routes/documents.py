"""
Document routes — THIN by design.

Each handler:
  1. Receives the HTTP request
  2. Delegates to DocumentService
  3. Returns a response schema

No SQL, no file I/O, no business logic here.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile

from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService
from app.dependencies import get_document_service

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    doc = await service.upload_document(file)
    return DocumentResponse.model_validate(doc.__dict__)


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    service: DocumentService = Depends(get_document_service),
) -> List[DocumentResponse]:
    docs = service.list_documents()
    return [DocumentResponse.model_validate(d.__dict__) for d in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    doc = service.get_document(document_id)
    return DocumentResponse.model_validate(doc.__dict__)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
) -> None:
    service.delete_document(document_id)
