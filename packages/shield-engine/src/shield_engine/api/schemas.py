"""Pydantic schemas for API boundary."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    clause_count: int


class AnalyzeResponse(BaseModel):
    id: str
    status: str
    analyzed_clauses: int


class ClausePositionSchema(BaseModel):
    page: int
    char_start: int
    char_end: int


class ClauseSchema(BaseModel):
    id: str
    index: int
    title: str
    text: str
    position: ClausePositionSchema


class AnalysisSchema(BaseModel):
    clause_id: str
    category: str
    risk_level: str
    explanation: str
    quoted_evidence: str
    detected_by: str
    requires_priority_review: bool
    discrepancy_reason: str | None = None


class ClauseDetailSchema(BaseModel):
    clause: ClauseSchema
    analysis: AnalysisSchema | None = None


class ReportSchema(BaseModel):
    id: str
    filename: str
    status: str
    disclaimer: str = Field(
        default=(
            "D4TA Shield es una segunda lectura antes de la firma, no sustituto de asesoría legal. "
            "Este informe señala patrones de riesgo en cláusulas individuales; la decisión final es siempre humana."
        )
    )
    clauses: list[ClauseSchema]
    analyses: list[AnalysisSchema]
    discrepancies: list[AnalysisSchema]
