"""Dependency injection for application services."""

import sqlite3
from pathlib import Path

from app.ai.gemini_provider import GeminiModelProvider
from app.agents.agent_context_builder import AgentContextBuilder
from app.agents.agent_manager import AgentManager
from app.ai.model_router import ModelRouter
from app.config.settings import settings
from app.repositories.chunk_sql_repository import SqlChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.approval_workflow_service import ApprovalWorkflowService
from app.services.deterministic_answer_generator import (
    DeterministicAnswerGenerator,
)
from app.services.document_chunker import DocumentChunker
from app.services.document_content_service import DocumentContentService
from app.services.document_normalizer import DocumentNormalizer
from app.services.document_service import DocumentService
from app.services.gemini_inspection_analyzer import GeminiInspectionAnalyzer
from app.services.knowledge_ingestion_service import KnowledgeIngestionService
from app.services.pdf_processing_pipeline import PdfProcessingPipeline
from app.services.pypdf_processor import PypdfProcessor
from app.services.query_embedding_service import QueryEmbeddingService
from app.services.rag_service import RagService
from app.services.sentence_transformer_embedding_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.services.tesseract_ocr_processor import TesseractOcrProcessor
from app.storage.local_storage import LocalStorage


def get_document_service() -> DocumentService:
    """Create a document service for the current request."""
    repository = DocumentRepository(db_path=settings.DATABASE_PATH)
    storage = LocalStorage(upload_dir=Path(settings.UPLOAD_DIR))
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    return DocumentService(
        repository=repository,
        storage=storage,
        max_upload_bytes=max_bytes,
    )


def get_document_content_service() -> DocumentContentService:
    """Create the document processing service."""
    return DocumentContentService(
        document_service=get_document_service(),
        pdf_pipeline=PdfProcessingPipeline(
            pdf_processor=PypdfProcessor(),
            ocr_processor=TesseractOcrProcessor(),
        ),
        normalizer=DocumentNormalizer(),
    )


def get_knowledge_ingestion_service():
    """Create and clean up the local knowledge-base ingestion service."""
    connection = sqlite3.connect(settings.DATABASE_PATH)

    try:
        chunk_repository = SqlChunkRepository(connection)
        embedding_repository = EmbeddingRepository(connection)

        yield KnowledgeIngestionService(
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
    finally:
        connection.close()


def get_rag_service():
    """Create and clean up the local RAG query service."""
    connection = sqlite3.connect(settings.DATABASE_PATH)

    try:
        chunk_repository = SqlChunkRepository(connection)
        embedding_repository = EmbeddingRepository(connection)

        yield RagService(
            chunk_repository=chunk_repository,
            embedding_repository=embedding_repository,
            query_embedding_service=QueryEmbeddingService(),
            answer_generator=DeterministicAnswerGenerator(),
        )
    finally:
        connection.close()


def get_agent_manager():
    """Create and clean up the grounded application agent manager."""
    connection = sqlite3.connect(settings.DATABASE_PATH)

    try:
        chunk_repository = SqlChunkRepository(connection)
        embedding_repository = EmbeddingRepository(connection)

        rag_service = RagService(
            chunk_repository=chunk_repository,
            embedding_repository=embedding_repository,
            query_embedding_service=QueryEmbeddingService(),
            answer_generator=DeterministicAnswerGenerator(),
        )

        context_builder = AgentContextBuilder(rag_service)

        gemini_provider = GeminiModelProvider()
        model_router = ModelRouter(providers=(gemini_provider,))

        yield AgentManager(
            model_router=model_router,
            context_builder=context_builder,
        )
    finally:
        connection.close()


def get_approval_workflow_service() -> ApprovalWorkflowService:
    """Create the inspection approval workflow service."""
    gemini_provider = GeminiModelProvider()

    return ApprovalWorkflowService(
        inspection_analyzer=GeminiInspectionAnalyzer(
            model_provider=gemini_provider,
        ),
    )
