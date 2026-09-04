"""OCR processing interface."""

from typing import Protocol

from app.models.document import Document
from app.models.ocr import OcrProcessingResult


class OcrProcessingError(RuntimeError):
    """Raised when OCR processing cannot be completed."""


class OcrProcessor(Protocol):
    """Interface implemented by concrete OCR engines."""

    def process(self, document: Document) -> OcrProcessingResult:
        """Run OCR against the supplied stored document."""
        ...