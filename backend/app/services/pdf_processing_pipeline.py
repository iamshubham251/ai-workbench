"""Orchestrate PDF text extraction and OCR."""

from app.models.document import Document
from app.models.ocr import OcrPage
from app.models.pdf_processing import (
    PdfContentType,
    PdfPage,
    PdfProcessingResult,
)
from app.services.ocr_processor import OcrProcessor
from app.services.pdf_processor import PdfProcessor


class PdfProcessingPipeline:
    """Combine embedded-text extraction with OCR when required."""

    def __init__(
        self,
        pdf_processor: PdfProcessor,
        ocr_processor: OcrProcessor,
    ) -> None:
        self.pdf_processor = pdf_processor
        self.ocr_processor = ocr_processor

    def process(self, document: Document) -> PdfProcessingResult:
        """Process a PDF using text extraction and OCR as appropriate."""
        extracted = self.pdf_processor.process(document)

        if extracted.content_type == PdfContentType.TEXT:
            return extracted

        if extracted.content_type == PdfContentType.EMPTY:
            if not extracted.pages:
                return extracted

            ocr_result = self.ocr_processor.process(document)

            pages = tuple(
                PdfPage(
                    page_number=page.page_number,
                    text=page.text,
                )
                for page in ocr_result.pages
            )

            return PdfProcessingResult(
                document_id=document.id,
                pages=pages,
                warnings=extracted.warnings + ocr_result.warnings,
                content_type=(
                    PdfContentType.SCANNED
                    if any(page.text.strip() for page in pages)
                    else PdfContentType.EMPTY
                ),
            )

        ocr_result = self.ocr_processor.process(document)

        if extracted.content_type == PdfContentType.SCANNED:
            pages = tuple(
                PdfPage(
                    page_number=page.page_number,
                    text=page.text,
                )
                for page in ocr_result.pages
            )

            return PdfProcessingResult(
                document_id=document.id,
                pages=pages,
                warnings=extracted.warnings + ocr_result.warnings,
                content_type=PdfContentType.SCANNED,
            )

        return self._merge_mixed_results(
            extracted,
            ocr_result.pages,
            ocr_result.warnings,
        )

    @staticmethod
    def _merge_mixed_results(
        extracted: PdfProcessingResult,
        ocr_pages: tuple[OcrPage, ...],
        ocr_warnings: tuple[str, ...],
    ) -> PdfProcessingResult:
        """Keep extracted text and fill sparse pages using OCR."""
        ocr_by_page = {
            page.page_number: page
            for page in ocr_pages
        }

        merged_pages: list[PdfPage] = []

        for page in extracted.pages:
            if page.text.strip():
                merged_pages.append(page)
                continue

            ocr_page = ocr_by_page.get(page.page_number)

            if ocr_page is None:
                merged_pages.append(page)
                continue

            merged_pages.append(
                PdfPage(
                    page_number=page.page_number,
                    text=ocr_page.text,
                )
            )

        return PdfProcessingResult(
            document_id=extracted.document_id,
            pages=tuple(merged_pages),
            warnings=extracted.warnings + ocr_warnings,
            content_type=PdfContentType.MIXED,
        )
