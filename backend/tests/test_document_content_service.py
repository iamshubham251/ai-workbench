from uuid import uuid4
from unittest.mock import Mock

from app.models.document_content import DocumentContent
from app.models.document import Document
from app.models.pdf_processing import PdfContentType, PdfPage, PdfProcessingResult
from app.services.document_content_service import DocumentContentService


def test_get_content_processes_and_normalizes_document():
    document_id = uuid4()
    document = Mock(spec=Document)
    document.id = document_id

    document_service = Mock()
    document_service.get_document.return_value = document

    pipeline = Mock()
    pipeline.process.return_value = PdfProcessingResult(
        document_id=document_id,
        pages=(
            PdfPage(page_number=1, text="  INSPECTION REPORT  "),
            PdfPage(page_number=2, text="Finding: belt damage"),
        ),
        content_type=PdfContentType.TEXT,
    )

    normalizer = Mock()
    expected = DocumentContent(
        document_id=document_id,
        pages=("INSPECTION REPORT", "Finding: belt damage"),
    )
    normalizer.normalize.return_value = expected

    service = DocumentContentService(
        document_service=document_service,
        pdf_pipeline=pipeline,
        normalizer=normalizer,
    )

    result = service.get_content(document_id)

    assert result is expected
    document_service.get_document.assert_called_once_with(document_id)
    pipeline.process.assert_called_once_with(document)
    normalizer.normalize.assert_called_once_with(pipeline.process.return_value)


def test_get_content_propagates_document_not_found_error():
    document_id = uuid4()

    document_service = Mock()
    document_service.get_document.side_effect = ValueError("Document not found")

    pipeline = Mock()
    normalizer = Mock()

    service = DocumentContentService(
        document_service=document_service,
        pdf_pipeline=pipeline,
        normalizer=normalizer,
    )

    try:
        service.get_content(document_id)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Document not found"

    pipeline.process.assert_not_called()
    normalizer.normalize.assert_not_called()
