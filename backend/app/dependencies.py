"""Dependency injection for application services."""

import sqlite3
from pathlib import Path

from app.ai.gemini_provider import GeminiModelProvider
from app.agents.agent_manager import AgentManager
from app.ai.model_router import ModelRouter
from app.config.settings import settings
from app.repositories.chunk_sql_repository import SqlChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.deterministic_answer_generator import (
    DeterministicAnswerGenerator,
)
from app.services.document_chunker import DocumentChunker
from app.services.document_normalizer import DocumentNormalizer
from app.services.document_service import DocumentService
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


def get_agent_manager() -> AgentManager:
    """Create the application agent manager with the configured Gemini provider."""
    gemini_provider = GeminiModelProvider()
    model_router = ModelRouter(providers=(gemini_provider,))

    return AgentManager(model_router=model_router)
