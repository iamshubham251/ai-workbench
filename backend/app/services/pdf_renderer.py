"""PDF page rendering service."""

from pathlib import Path
from typing import Protocol

import pymupdf

from app.models.document import Document


class PdfRenderingError(RuntimeError):
    """Raised when a PDF cannot be rendered."""


class PdfRenderer(Protocol):
    """Interface for rendering PDF pages into images."""

    def render_page(
        self,
        document: Document,
        page_number: int,
    ) -> bytes:
        """Render one one-based PDF page as PNG bytes."""
        ...


class PyMuPdfRenderer:
    """Render PDF pages to PNG images using PyMuPDF."""

    def __init__(self, dpi: int = 200) -> None:
        if dpi <= 0:
            raise ValueError("dpi must be positive")

        self.dpi = dpi

    def render_page(
        self,
        document: Document,
        page_number: int,
    ) -> bytes:
        """Render one one-based PDF page to PNG bytes."""
        if page_number < 1:
            raise ValueError("page_number must be one-based")

        source_path = Path(document.storage_path)

        if not source_path.is_file():
            raise PdfRenderingError("PDF source is unavailable")

        try:
            with pymupdf.open(source_path) as pdf:
                if page_number > len(pdf):
                    raise PdfRenderingError(
                        f"PDF does not contain page {page_number}"
                    )

                page = pdf[page_number - 1]

                zoom = self.dpi / 72
                matrix = pymupdf.Matrix(zoom, zoom)

                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                return pixmap.tobytes("png")

        except PdfRenderingError:
            raise
        except (OSError, RuntimeError) as exc:
            raise PdfRenderingError(
                "PDF page could not be rendered"
            ) from exc