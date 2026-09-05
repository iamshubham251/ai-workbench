"""Build normalized document content from stored documents."""

from uuid import UUID

from app.models.document_content import DocumentContent
from app.services.document_service import DocumentService
from app.services.document_normalizer import DocumentNormalizer
from app.services.pdf_processing_pipeline import PdfProcessingPipeline


class DocumentContentService:
    """Process a stored document into normalized downstream content."""

    def __init__(
        self,
        document_service: DocumentService,
        pdf_pipeline: PdfProcessingPipeline,
        normalizer: DocumentNormalizer,
    ) -> None:
        self._document_service = document_service
        self._pdf_pipeline = pdf_pipeline
        self._normalizer = normalizer

    def get_content(self, document_id: UUID) -> DocumentContent:
        """Load, process, and normalize a stored document."""
        document = self._document_service.get_document(document_id)
        result = self._pdf_pipeline.process(document)
        return self._normalizer.normalize(result)
