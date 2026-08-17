"""SQLite persistence for contracts and analysis results."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from shield_engine.config import settings
from shield_engine.models import (
    Clause,
    ClauseAnalysis,
    ClauseCategory,
    ClausePosition,
    ContractRecord,
    ContractStatus,
    DetectionLayer,
    LlmFinding,
    RiskLevel,
    RuleFinding,
    new_id,
    utcnow,
)


class ContractStore:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.sqlite_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS contracts (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    full_text TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS clauses (
                    id TEXT PRIMARY KEY,
                    contract_id TEXT NOT NULL,
                    idx INTEGER NOT NULL,
                    title TEXT,
                    text TEXT NOT NULL,
                    page INTEGER,
                    char_start INTEGER,
                    char_end INTEGER,
                    section_label TEXT,
                    FOREIGN KEY (contract_id) REFERENCES contracts(id)
                );
                CREATE TABLE IF NOT EXISTS analyses (
                    clause_id TEXT PRIMARY KEY,
                    contract_id TEXT NOT NULL,
                    category TEXT,
                    risk_level TEXT,
                    explanation TEXT,
                    quoted_evidence TEXT,
                    detected_by TEXT,
                    requires_priority_review INTEGER,
                    discrepancy_reason TEXT,
                    rule_json TEXT,
                    llm_json TEXT,
                    FOREIGN KEY (contract_id) REFERENCES contracts(id)
                );
                """
            )

    def save(self, contract: ContractRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO contracts
                (id, filename, content_type, status, file_path, full_text, error_message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contract.id,
                    contract.filename,
                    contract.content_type,
                    contract.status.value,
                    contract.file_path,
                    contract.full_text,
                    contract.error_message,
                    contract.created_at.isoformat(),
                    contract.updated_at.isoformat(),
                ),
            )
            conn.execute("DELETE FROM clauses WHERE contract_id = ?", (contract.id,))
            for clause in contract.clauses:
                conn.execute(
                    """
                    INSERT INTO clauses (id, contract_id, idx, title, text, page, char_start, char_end, section_label)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        clause.id,
                        clause.contract_id,
                        clause.index,
                        clause.title,
                        clause.text,
                        clause.position.page,
                        clause.position.char_start,
                        clause.position.char_end,
                        clause.section_label,
                    ),
                )
            conn.execute("DELETE FROM analyses WHERE contract_id = ?", (contract.id,))
            for analysis in contract.analyses:
                conn.execute(
                    """
                    INSERT INTO analyses
                    (clause_id, contract_id, category, risk_level, explanation, quoted_evidence,
                     detected_by, requires_priority_review, discrepancy_reason, rule_json, llm_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        analysis.clause_id,
                        contract.id,
                        analysis.category.value,
                        analysis.risk_level.value,
                        analysis.explanation,
                        analysis.quoted_evidence,
                        analysis.detected_by.value,
                        1 if analysis.requires_priority_review else 0,
                        analysis.discrepancy_reason,
                        json.dumps(_rule_to_dict(analysis.rule_finding)),
                        json.dumps(_llm_to_dict(analysis.llm_finding)),
                    ),
                )

    def get(self, contract_id: str) -> ContractRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,)).fetchone()
            if not row:
                return None
            contract = _row_to_contract(row)
            clause_rows = conn.execute(
                "SELECT * FROM clauses WHERE contract_id = ? ORDER BY idx", (contract_id,)
            ).fetchall()
            contract.clauses = [_row_to_clause(r) for r in clause_rows]
            analysis_rows = conn.execute(
                "SELECT * FROM analyses WHERE contract_id = ?", (contract_id,)
            ).fetchall()
            contract.analyses = [_row_to_analysis(r) for r in analysis_rows]
            return contract

    def list_contracts(self) -> list[ContractRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM contracts ORDER BY created_at DESC").fetchall()
            return [_row_to_contract(r) for r in rows]


def _row_to_contract(row: sqlite3.Row) -> ContractRecord:
    return ContractRecord(
        id=row["id"],
        filename=row["filename"],
        content_type=row["content_type"],
        status=ContractStatus(row["status"]),
        file_path=row["file_path"],
        full_text=row["full_text"] or "",
        error_message=row["error_message"],
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row["updated_at"]),
    )


def _row_to_clause(row: sqlite3.Row) -> Clause:
    return Clause(
        id=row["id"],
        contract_id=row["contract_id"],
        index=row["idx"],
        title=row["title"] or "",
        text=row["text"],
        position=ClausePosition(
            page=row["page"] or 1,
            char_start=row["char_start"] or 0,
            char_end=row["char_end"] or len(row["text"]),
        ),
        section_label=row["section_label"] or "",
    )


def _row_to_analysis(row: sqlite3.Row) -> ClauseAnalysis:
    rule_data = json.loads(row["rule_json"]) if row["rule_json"] else None
    llm_data = json.loads(row["llm_json"]) if row["llm_json"] else None
    return ClauseAnalysis(
        clause_id=row["clause_id"],
        category=ClauseCategory(row["category"]),
        risk_level=RiskLevel(row["risk_level"]),
        explanation=row["explanation"] or "",
        quoted_evidence=row["quoted_evidence"] or "",
        detected_by=DetectionLayer(row["detected_by"]),
        requires_priority_review=bool(row["requires_priority_review"]),
        discrepancy_reason=row["discrepancy_reason"],
        rule_finding=_dict_to_rule(rule_data) if rule_data else None,
        llm_finding=_dict_to_llm(llm_data) if llm_data else None,
    )


def _parse_dt(value: str):
    from datetime import datetime

    return datetime.fromisoformat(value)


def _rule_to_dict(rule: RuleFinding | None) -> dict[str, Any] | None:
    if not rule:
        return None
    return {
        "category": rule.category.value,
        "risk_level": rule.risk_level.value,
        "explanation": rule.explanation,
        "quoted_evidence": rule.quoted_evidence,
        "rule_name": rule.rule_name,
    }


def _llm_to_dict(llm: LlmFinding | None) -> dict[str, Any] | None:
    if not llm:
        return None
    return {
        "category": llm.category.value,
        "risk_level": llm.risk_level.value,
        "explanation": llm.explanation,
        "quoted_evidence": llm.quoted_evidence,
        "inconclusive": llm.inconclusive,
    }


def _dict_to_rule(data: dict[str, Any]) -> RuleFinding:
    return RuleFinding(
        category=ClauseCategory(data["category"]),
        risk_level=RiskLevel(data["risk_level"]),
        explanation=data["explanation"],
        quoted_evidence=data["quoted_evidence"],
        rule_name=data.get("rule_name", ""),
    )


def _dict_to_llm(data: dict[str, Any]) -> LlmFinding:
    return LlmFinding(
        category=ClauseCategory(data["category"]),
        risk_level=RiskLevel(data["risk_level"]),
        explanation=data["explanation"],
        quoted_evidence=data["quoted_evidence"],
        inconclusive=data.get("inconclusive", False),
    )


store = ContractStore()
