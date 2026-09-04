"""Tesseract-backed OCR processing."""

from io import BytesIO
from pathlib import Path
from shutil import which

import pymupdf
import pytesseract
from PIL import Image
from pytesseract import Output

from app.models.document import Document
from app.models.ocr import OcrPage, OcrProcessingResult
from app.services.ocr_processor import (
    OcrProcessingError,
    OcrProcessor,
)


class TesseractOcrProcessor:
    """Run OCR on PDF pages using PyMuPDF and Tesseract."""

    def __init__(
        self,
        dpi: int = 200,
        tesseract_cmd: str | None = None,
        language: str = "eng",
    ) -> None:
        if dpi <= 0:
            raise ValueError("dpi must be positive")

        if not language.strip():
            raise ValueError("language must not be empty")

        if tesseract_cmd:
            resolved_tesseract = Path(tesseract_cmd)

            if not resolved_tesseract.is_file():
                raise OcrProcessingError(
                    "Tesseract executable could not be found"
                )

            resolved_tesseract_path = str(resolved_tesseract)
        else:
            resolved_tesseract_path = which("tesseract")

            if not resolved_tesseract_path:
                raise OcrProcessingError(
                    "Tesseract executable could not be found"
                )

        self.dpi = dpi
        self.tesseract_cmd = resolved_tesseract_path
        self.language = language

        pytesseract.pytesseract.tesseract_cmd = resolved_tesseract_path

    def process(self, document: Document) -> OcrProcessingResult:
        """Run OCR against every page of a stored PDF."""
        source_path = Path(document.storage_path)

        if not source_path.is_file():
            raise OcrProcessingError(
                "OCR source document is unavailable"
            )

        try:
            with pymupdf.open(source_path) as pdf:
                pages: list[OcrPage] = []
                warnings: list[str] = []

                for page_number in range(1, len(pdf) + 1):
                    page = pdf[page_number - 1]

                    try:
                        text, confidence = self._ocr_page(page)
                    except Exception:
                        warnings.append(
                            f"Page {page_number}: OCR failed"
                        )
                        pages.append(
                            OcrPage(
                                page_number=page_number,
                                text="",
                                confidence=None,
                            )
                        )
                        continue

                    pages.append(
                        OcrPage(
                            page_number=page_number,
                            text=text,
                            confidence=confidence,
                        )
                    )

                return OcrProcessingResult(
                    document_id=document.id,
                    pages=tuple(pages),
                    warnings=tuple(warnings),
                )

        except OcrProcessingError:
            raise
        except (OSError, RuntimeError) as exc:
            raise OcrProcessingError(
                "OCR source document could not be read"
            ) from exc

    def _ocr_page(
        self,
        page: pymupdf.Page,
    ) -> tuple[str, float | None]:
        """Render and OCR one PDF page."""
        zoom = self.dpi / 72
        matrix = pymupdf.Matrix(zoom, zoom)

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False,
        )

        image = Image.open(
            BytesIO(pixmap.tobytes("png"))
        )

        data = pytesseract.image_to_data(
            image,
            lang=self.language,
            output_type=Output.DICT,
        )

        text_parts: list[str] = []
        confidences: list[float] = []

        for text, confidence in zip(
            data["text"],
            data["conf"],
        ):
            normalized_text = text.strip()

            if not normalized_text:
                continue

            text_parts.append(normalized_text)

            try:
                numeric_confidence = float(confidence)
            except (TypeError, ValueError):
                continue

            if numeric_confidence >= 0:
                confidences.append(
                    numeric_confidence / 100.0
                )

        text = " ".join(text_parts)

        confidence = (
            sum(confidences) / len(confidences)
            if confidences
            else None
        )

        return text, confidence