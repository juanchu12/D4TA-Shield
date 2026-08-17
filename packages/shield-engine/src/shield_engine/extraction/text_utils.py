"""Text normalization utilities."""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"(\w)-\n(\w)", r"\1\2", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def page_texts_from_full(full_text: str, page_markers: list[tuple[int, int, int]] | None = None) -> list[str]:
    """Split full text into pages if markers provided as (page_num, start, end)."""
    if not page_markers:
        return [full_text]
    pages: list[str] = []
    for _, start, end in sorted(page_markers, key=lambda m: m[0]):
        pages.append(full_text[start:end])
    return pages
