"""Ingest documents into the local RAG knowledge base."""

from dataclasses import dataclass
from uuid import UUID

from app.models.document_chunk import DocumentChunk
from app.models.document_content import DocumentContent
from app.models.embedding import DocumentEmbedding
from app.models.document import Document
from app.repositories.chunk_sql_repository import SqlChunkRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.document_chunker import DocumentChunker
from app.services.document_normalizer import DocumentNormalizer
from app.services.embedding_provider import EmbeddingProvider
from app.services.pdf_processing_pipeline import PdfProcessingPipeline


@dataclass(frozen=True)
class KnowledgeIngestionResult:
    """Summary of a document successfully added to the knowledge base."""

    document_id: UUID
    chunk_count: int
    embedding_count: int


class KnowledgeIngestionService:
    """Run the complete document-to-knowledge-base pipeline."""

    def __init__(
        self,
        pdf_pipeline: PdfProcessingPipeline,
        normalizer: DocumentNormalizer,
        chunker: DocumentChunker,
        embedding_provider: EmbeddingProvider,
        chunk_repository: SqlChunkRepository,
        embedding_repository: EmbeddingRepository,
    ) -> None:
        self.pdf_pipeline = pdf_pipeline
        self.normalizer = normalizer
        self.chunker = chunker
        self.embedding_provider = embedding_provider
        self.chunk_repository = chunk_repository
        self.embedding_repository = embedding_repository

    def ingest(self, document: Document) -> KnowledgeIngestionResult:
        """Process and persist a document for semantic retrieval."""

        processing_result = self.pdf_pipeline.process(document)

        content: DocumentContent = self.normalizer.normalize(
            processing_result
        )

        chunks: tuple[DocumentChunk, ...] = self.chunker.chunk(content)

        embeddings: tuple[DocumentEmbedding, ...] = (
            self.embedding_provider.embed_batch(chunks)
        )

        self.chunk_repository.save(
            document.id,
            chunks,
        )

        self.embedding_repository.save(
            document.id,
            embeddings,
        )

        return KnowledgeIngestionResult(
            document_id=document.id,
            chunk_count=len(chunks),
            embedding_count=len(embeddings),
        )

    def get_status(self, document_id: UUID) -> KnowledgeIngestionResult:
        """Return persisted indexing status for a document."""

        chunk_count = self.chunk_repository.count_by_document_id(
            document_id
        )
        embedding_count = self.embedding_repository.count_by_document_id(
            document_id
        )

        return KnowledgeIngestionResult(
            document_id=document_id,
            chunk_count=chunk_count,
            embedding_count=embedding_count,
        )
