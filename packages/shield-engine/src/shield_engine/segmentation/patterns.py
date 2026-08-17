"""Regex patterns for contract clause boundaries."""

from __future__ import annotations

import re

CLAUSE_START_PATTERNS = [
    re.compile(r"^(?:CL[AÁ]USULA|CLAUSULA|ART[IÍ]CULO|ARTICULO)\s+(?:PRIMERA|SEGUNDA|TERCERA|\d+|[IVXLC]+)", re.I | re.M),
    re.compile(r"^(?:CAP[IÍ]TULO|CAPITULO|SECCI[OÓ]N|SECCION)\s+[\dIVXLC\.]+", re.I | re.M),
    re.compile(r"^\d+(?:\.\d+){0,3}\.?\s+[A-ZÁÉÍÓÚÑ]", re.M),
    re.compile(r"^[IVXLC]+\.\s+[A-ZÁÉÍÓÚÑ]", re.M),
]

TITLE_LINE = re.compile(r"^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\-]{4,80}$", re.M)
