import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.models.document import Document
from app.repositories.chunk_sql_repository import SqlChunkRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.document_chunker import DocumentChunker
from app.services.document_normalizer import DocumentNormalizer
from app.services.knowledge_ingestion_service import KnowledgeIngestionService
from app.services.pdf_processing_pipeline import PdfProcessingPipeline
from app.services.pypdf_processor import PypdfProcessor
from app.services.sentence_transformer_embedding_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.services.tesseract_ocr_processor import TesseractOcrProcessor


def test_knowledge_ingestion_creates_chunks_and_embeddings(tmp_path):
    pdf_path = Path(tmp_path) / "sop.pdf"

    # Create a minimal valid PDF using PyMuPDF.
    import fitz

    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text(
        (72, 72),
        (
            "Conveyor Belt Inspection SOP\n\n"
            "Inspect the conveyor belt before starting daily operations. "
            "Check belt alignment, joints, tension, and visible damage."
        ),
    )
    pdf.save(pdf_path)
    pdf.close()

    document_id = uuid4()

    document = Document(
        id=document_id,
        original_filename="sop.pdf",
        stored_filename="sop.pdf",
        content_type="application/pdf",
        extension=".pdf",
        size_bytes=pdf_path.stat().st_size,
        status="uploaded",
        storage_path=str(pdf_path),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    connection = sqlite3.connect(":memory:")

    chunk_repository = SqlChunkRepository(connection)
    embedding_repository = EmbeddingRepository(connection)

    service = KnowledgeIngestionService(
        pdf_pipeline=PdfProcessingPipeline(
            pdf_processor=PypdfProcessor(),
            ocr_processor=TesseractOcrProcessor(),
        ),
        normalizer=DocumentNormalizer(),
        chunker=DocumentChunker(),
        embedding_provider=SentenceTransformerEmbeddingProvider(),
        chunk_repository=chunk_repository,
        embedding_repository=embedding_repository,
    )

    result = service.ingest(document)

    assert result.document_id == document_id
    assert result.chunk_count > 0
    assert result.embedding_count == result.chunk_count

    stored_chunks = chunk_repository.get_by_document_id(document_id)
    stored_embeddings = embedding_repository.get_by_document_id(document_id)

    assert len(stored_chunks) == result.chunk_count
    assert len(stored_embeddings) == result.embedding_count
    assert stored_chunks[0].text
    assert stored_embeddings[0].dimensions == 384

    connection.close()
