"""DOCX extraction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from docx import Document

from shield_engine.extraction.text_utils import clean_text


@dataclass
class ExtractedPage:
    page_number: int
    text: str
    loader: str = "docx"


def load_docx(docx_path: Path) -> tuple[str, list[ExtractedPage]]:
    doc = Document(str(docx_path))
    paragraphs = [clean_text(p.text) for p in doc.paragraphs if clean_text(p.text)]
    if not paragraphs:
        raise ValueError(f"{docx_path.name}: empty DOCX")
    full_text = "\n\n".join(paragraphs)
    return full_text, [ExtractedPage(page_number=1, text=full_text, loader="docx")]
