"""PDF extraction cascade: PyPDF → pdfplumber → PyMuPDF → OCR."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from shield_engine.config import settings
from shield_engine.extraction.text_utils import clean_text

logger = logging.getLogger(__name__)


@dataclass
class ExtractedPage:
    page_number: int
    text: str
    loader: str


def _load_with_pdfplumber(pdf_path: Path) -> list[ExtractedPage]:
    import pdfplumber

    pages: list[ExtractedPage] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for index, page in enumerate(pdf.pages):
            text = clean_text(page.extract_text() or "")
            if text:
                pages.append(ExtractedPage(page_number=index + 1, text=text, loader="pdfplumber"))
    return pages


def _load_with_pymupdf(pdf_path: Path) -> list[ExtractedPage]:
    try:
        import fitz
    except ImportError:
        return []

    pages: list[ExtractedPage] = []
    doc = fitz.open(str(pdf_path))
    for index in range(len(doc)):
        text = clean_text(doc[index].get_text("text") or "")
        if text:
            pages.append(ExtractedPage(page_number=index + 1, text=text, loader="pymupdf"))
    doc.close()
    return pages


def _load_with_ocr(pdf_path: Path) -> list[ExtractedPage]:
    if not settings.enable_ocr:
        return []
    try:
        import fitz
        import pytesseract
        from PIL import Image
    except ImportError:
        logger.warning("OCR dependencies unavailable")
        return []

    pages: list[ExtractedPage] = []
    doc = fitz.open(str(pdf_path))
    for index in range(len(doc)):
        pix = doc[index].get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = clean_text(pytesseract.image_to_string(img, lang=settings.ocr_lang))
        if text:
            pages.append(ExtractedPage(page_number=index + 1, text=text, loader="ocr"))
    doc.close()
    return pages


def load_pdf(pdf_path: Path) -> tuple[str, list[ExtractedPage]]:
    """Return concatenated full text and per-page records."""
    pages: list[ExtractedPage] = []
    try:
        reader = PdfReader(str(pdf_path))
        for index, page in enumerate(reader.pages):
            text = clean_text(page.extract_text() or "")
            if text:
                pages.append(ExtractedPage(page_number=index + 1, text=text, loader="pypdf"))
    except Exception as exc:
        logger.warning("PyPDF failed for %s: %s", pdf_path.name, exc)

    if not pages:
        pages = _load_with_pdfplumber(pdf_path)
    if not pages:
        pages = _load_with_pymupdf(pdf_path)
    if not pages:
        pages = _load_with_ocr(pdf_path)

    if not pages:
        raise ValueError(f"{pdf_path.name}: no extractable text (scanned PDF?)")

    full_text = "\n\n".join(p.text for p in pages)
    return full_text, pages
