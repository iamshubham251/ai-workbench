"""Dependency injection for application services."""

from pathlib import Path

from app.agents.agent_context_builder import AgentContextBuilder
from app.agents.agent_manager import AgentManager
from app.ai.gemini_provider import GeminiModelProvider
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
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_auth_service() -> AuthService:
    return AuthService(user_repository=UserRepository())

def get_current_user(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = auth_service.user_repository.get_by_email(email=email)
    if user is None:
        raise credentials_exception
    return user

def get_document_service() -> DocumentService:
    """Create a document service for the current request."""
    repository = DocumentRepository()
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
            ocr_processor=TesseractOcrProcessor(
                tesseract_cmd=settings.TESSERACT_CMD or None
            ),
        ),
        normalizer=DocumentNormalizer(),
    )


def get_knowledge_ingestion_service():
    """Create and clean up the local knowledge-base ingestion service."""
    chunk_repository = SqlChunkRepository()
    embedding_repository = EmbeddingRepository()

    yield KnowledgeIngestionService(
        pdf_pipeline=PdfProcessingPipeline(
            pdf_processor=PypdfProcessor(),
            ocr_processor=TesseractOcrProcessor(
                tesseract_cmd=settings.TESSERACT_CMD or None
            ),
        ),
        normalizer=DocumentNormalizer(),
        chunker=DocumentChunker(),
        embedding_provider=SentenceTransformerEmbeddingProvider(),
        chunk_repository=chunk_repository,
        embedding_repository=embedding_repository,
    )


def get_rag_service():
    """Create and clean up the local RAG query service."""
    chunk_repository = SqlChunkRepository()
    embedding_repository = EmbeddingRepository()
    document_repository = DocumentRepository()

    yield RagService(
        chunk_repository=chunk_repository,
        embedding_repository=embedding_repository,
        document_repository=document_repository,
        query_embedding_service=QueryEmbeddingService(),
        answer_generator=DeterministicAnswerGenerator(),
    )


def get_agent_manager():
    """Create and clean up the grounded application agent manager."""
    chunk_repository = SqlChunkRepository()
    embedding_repository = EmbeddingRepository()
    document_repository = DocumentRepository()

    rag_service = RagService(
        chunk_repository=chunk_repository,
        embedding_repository=embedding_repository,
        document_repository=document_repository,
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


def get_approval_workflow_service():
    """Create and clean up the inspection approval workflow service."""
    chunk_repository = SqlChunkRepository()
    embedding_repository = EmbeddingRepository()
    document_repository = DocumentRepository()

    rag_service = RagService(
        chunk_repository=chunk_repository,
        embedding_repository=embedding_repository,
        document_repository=document_repository,
        query_embedding_service=QueryEmbeddingService(),
        answer_generator=DeterministicAnswerGenerator(),
    )

    gemini_provider = GeminiModelProvider()

    yield ApprovalWorkflowService(
        inspection_analyzer=GeminiInspectionAnalyzer(
            model_provider=gemini_provider,
        ),
        document_content_service=get_document_content_service(),
        rag_service=rag_service,
    )
