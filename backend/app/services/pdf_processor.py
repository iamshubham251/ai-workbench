"""Service boundary for PDF processing implementations."""

from typing import Protocol

from app.models.document import Document
from app.models.pdf_processing import PdfProcessingResult


class PdfProcessor(Protocol):
    """Extract text from a stored PDF without owning storage or persistence."""

    def process(self, document: Document) -> PdfProcessingResult:
        """Return extracted page text for *document*.

        A concrete implementation is intentionally deferred to Phase 4.1.2.
        """
        ...
