"""Structure-based clause segmentation."""

from __future__ import annotations

import re

from shield_engine.models import Clause, ClausePosition, new_id
from shield_engine.segmentation.patterns import CLAUSE_START_PATTERNS, TITLE_LINE


def _find_clause_starts(text: str) -> list[tuple[int, str]]:
    starts: dict[int, str] = {}
    for pattern in CLAUSE_START_PATTERNS:
        for match in pattern.finditer(text):
            line_start = text.rfind("\n", 0, match.start()) + 1
            line = text[line_start : text.find("\n", match.start())].strip()
            if len(line) >= 4:
                starts.setdefault(line_start, line[:120])
    if not starts:
        for match in TITLE_LINE.finditer(text):
            starts.setdefault(match.start(), match.group(0).strip()[:120])
    return sorted(starts.items(), key=lambda x: x[0])


def _estimate_page(char_offset: int, page_offsets: list[tuple[int, int, int]]) -> int:
    for page_num, start, end in page_offsets:
        if start <= char_offset < end:
            return page_num
    return page_offsets[-1][0] if page_offsets else 1


def segment_clauses(
    contract_id: str,
    full_text: str,
    page_offsets: list[tuple[int, int, int]] | None = None,
) -> list[Clause]:
    """Segment document into complete clauses with position metadata."""
    text = full_text.strip()
    if not text:
        return []

    page_offsets = page_offsets or [(1, 0, len(text))]
    starts = _find_clause_starts(text)

    if not starts:
        return [
            Clause(
                id=new_id(),
                contract_id=contract_id,
                index=0,
                title="Documento completo",
                text=text,
                position=ClausePosition(page=1, char_start=0, char_end=len(text)),
            )
        ]

    clauses: list[Clause] = []
    for idx, (start, title) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(text)
        body = text[start:end].strip()
        if len(body) < 20:
            continue
        clauses.append(
            Clause(
                id=new_id(),
                contract_id=contract_id,
                index=len(clauses),
                title=title,
                text=body,
                position=ClausePosition(
                    page=_estimate_page(start, page_offsets),
                    char_start=start,
                    char_end=end,
                ),
                section_label=title,
            )
        )
    return clauses


def build_page_offsets(pages: list[tuple[int, str]]) -> list[tuple[int, int, int]]:
    """Build (page_number, char_start, char_end) from page texts."""
    offsets: list[tuple[int, int, int]] = []
    cursor = 0
    for page_num, page_text in pages:
        start = cursor
        cursor += len(page_text) + 2
        offsets.append((page_num, start, cursor))
    return offsets
