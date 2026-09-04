"""Concrete PDF text extraction backed by pypdf."""

from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.models.document import Document
from app.models.pdf_processing import PdfPage, PdfProcessingResult
from app.services.pdf_processor import PdfProcessor


class PdfProcessingError(RuntimeError):
    """Raised when a PDF source cannot be opened or read."""


class PypdfProcessor(PdfProcessor):
    """Extract page text from a stored PDF without modifying it."""

    def process(self, document: Document) -> PdfProcessingResult:
        source_path = Path(document.storage_path)
        if not source_path.is_file():
            raise PdfProcessingError("PDF source is unavailable")

        try:
            reader = PdfReader(source_path)
        except (OSError, PdfReadError) as exc:
            raise PdfProcessingError("PDF source could not be read") from exc

        pages: list[PdfPage] = []
        warnings: list[str] = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
                warnings.append(
                    f"Page {page_number}: text could not be extracted"
                )
            pages.append(PdfPage(page_number=page_number, text=text))

        return PdfProcessingResult(
            document_id=document.id,
            pages=tuple(pages),
            warnings=tuple(warnings),
        )
