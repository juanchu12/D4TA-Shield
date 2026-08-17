"""Domain models for contract analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class ContractStatus(str, Enum):
    UPLOADED = "uploaded"
    SEGMENTED = "segmented"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class RiskLevel(str, Enum):
    LOW = "bajo"
    MEDIUM = "medio"
    HIGH = "alto"


class ClauseCategory(str, Enum):
    LIABILITY = "responsabilidad"
    INDEMNITY = "indemnizacion"
    TERMINATION = "terminacion"
    RENEWAL = "renovacion"
    JURISDICTION = "jurisdiccion"
    IP = "propiedad_intelectual"
    CONFIDENTIALITY = "confidencialidad"
    NON_COMPETE = "no_competencia"
    EXCLUSIVITY = "exclusividad"
    PENALTIES = "penalizaciones"
    FORCE_MAJEURE = "fuerza_mayor"
    OTHER = "otros"


class DetectionLayer(str, Enum):
    RULE = "rule"
    LLM = "llm"
    BOTH = "both"


def new_id() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ClausePosition:
    page: int
    char_start: int
    char_end: int


@dataclass
class Clause:
    id: str
    contract_id: str
    index: int
    title: str
    text: str
    position: ClausePosition
    section_label: str = ""


@dataclass
class RuleFinding:
    category: ClauseCategory
    risk_level: RiskLevel
    explanation: str
    quoted_evidence: str
    rule_name: str


@dataclass
class LlmFinding:
    category: ClauseCategory
    risk_level: RiskLevel
    explanation: str
    quoted_evidence: str
    inconclusive: bool = False


@dataclass
class ClauseAnalysis:
    clause_id: str
    category: ClauseCategory
    risk_level: RiskLevel
    explanation: str
    quoted_evidence: str
    detected_by: DetectionLayer
    requires_priority_review: bool
    rule_finding: RuleFinding | None = None
    llm_finding: LlmFinding | None = None
    discrepancy_reason: str | None = None


@dataclass
class ContractRecord:
    id: str
    filename: str
    content_type: str
    status: ContractStatus
    file_path: str
    full_text: str = ""
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    error_message: str | None = None
    clauses: list[Clause] = field(default_factory=list)
    analyses: list[ClauseAnalysis] = field(default_factory=list)

    def to_summary(self) -> dict[str, Any]:
        counts = {"bajo": 0, "medio": 0, "alto": 0}
        discrepancies = 0
        for a in self.analyses:
            counts[a.risk_level.value] = counts.get(a.risk_level.value, 0) + 1
            if a.requires_priority_review:
                discrepancies += 1
        return {
            "id": self.id,
            "filename": self.filename,
            "status": self.status.value,
            "clause_count": len(self.clauses),
            "risk_counts": counts,
            "discrepancy_count": discrepancies,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
