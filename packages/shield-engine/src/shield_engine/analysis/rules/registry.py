"""Deterministic rule-based risk detection."""

from __future__ import annotations

import re
from typing import Callable

from shield_engine.models import Clause, ClauseCategory, RiskLevel, RuleFinding

RuleFn = Callable[[Clause], RuleFinding | None]


def _match_evidence(text: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    start = max(0, match.start() - 40)
    end = min(len(text), match.end() + 40)
    return text[start:end].strip()


def rule_unlimited_liability(clause: Clause) -> RuleFinding | None:
    patterns = [
        re.compile(r"sin\s+l[ií]mite\s+de\s+responsabilidad", re.I),
        re.compile(r"responsabilidad\s+(?:ilimitada|sin\s+l[ií]mite)", re.I),
        re.compile(r"unlimited\s+liability", re.I),
    ]
    for pat in patterns:
        evidence = _match_evidence(clause.text, pat)
        if evidence:
            return RuleFinding(
                category=ClauseCategory.LIABILITY,
                risk_level=RiskLevel.HIGH,
                explanation="Detectada cláusula de responsabilidad sin límite explícito.",
                quoted_evidence=evidence,
                rule_name="unlimited_liability",
            )
    return None


def rule_liability_cap(clause: Clause) -> RuleFinding | None:
    pat = re.compile(
        r"(?:l[ií]mite|limit(?:e|ation)|cap)\s+(?:de\s+)?responsabilidad[^\d]{0,40}(\d[\d\.,]*)\s*(?:€|eur|usd|\$|euros?)",
        re.I,
    )
    evidence = _match_evidence(clause.text, pat)
    if evidence:
        return RuleFinding(
            category=ClauseCategory.LIABILITY,
            risk_level=RiskLevel.MEDIUM,
            explanation="Se detectó un límite de responsabilidad numérico — revisar si es proporcional.",
            quoted_evidence=evidence,
            rule_name="liability_cap",
        )
    return None


def rule_auto_renewal(clause: Clause) -> RuleFinding | None:
    patterns = [
        re.compile(r"renovaci[oó]n\s+(?:autom[aá]tica|t[aá]cita)", re.I),
        re.compile(r"pr[oó]rroga\s+autom[aá]tica", re.I),
        re.compile(r"automatic(?:ally)?\s+renew", re.I),
    ]
    for pat in patterns:
        evidence = _match_evidence(clause.text, pat)
        if evidence:
            return RuleFinding(
                category=ClauseCategory.RENEWAL,
                risk_level=RiskLevel.MEDIUM,
                explanation="Renovación automática o tácita detectada — verificar plazos de preaviso.",
                quoted_evidence=evidence,
                rule_name="auto_renewal",
            )
    return None


def rule_short_notice(clause: Clause) -> RuleFinding | None:
    pat = re.compile(r"preaviso\s+de\s+(\d{1,2})\s+d[ií]as", re.I)
    match = pat.search(clause.text)
    if match and int(match.group(1)) <= 15:
        evidence = _match_evidence(clause.text, pat)
        return RuleFinding(
            category=ClauseCategory.TERMINATION,
            risk_level=RiskLevel.MEDIUM,
            explanation=f"Preaviso de terminación corto ({match.group(1)} días).",
            quoted_evidence=evidence or match.group(0),
            rule_name="short_notice",
        )
    return None


def rule_foreign_jurisdiction(clause: Clause) -> RuleFinding | None:
    pat = re.compile(
        r"(?:jurisdicci[oó]n|fuero|tribunales?\s+de)\s+(?:de\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)",
        re.I,
    )
    evidence = _match_evidence(clause.text, pat)
    if evidence:
        return RuleFinding(
            category=ClauseCategory.JURISDICTION,
            risk_level=RiskLevel.MEDIUM,
            explanation="Cláusula de jurisdicción/fuero detectada — confirmar conveniencia.",
            quoted_evidence=evidence,
            rule_name="foreign_jurisdiction",
        )
    return None


def rule_penalty(clause: Clause) -> RuleFinding | None:
    pat = re.compile(
        r"(?:penalizaci[oó]n|multa|indemnizaci[oó]n\s+por\s+incumplimiento)[^\d]{0,30}(\d[\d\.,]*)\s*(?:%|€|eur|usd|\$)",
        re.I,
    )
    evidence = _match_evidence(clause.text, pat)
    if evidence:
        return RuleFinding(
            category=ClauseCategory.PENALTIES,
            risk_level=RiskLevel.HIGH,
            explanation="Penalización o multa con cifra explícita detectada.",
            quoted_evidence=evidence,
            rule_name="penalty_amount",
        )
    return None


def rule_exclusivity(clause: Clause) -> RuleFinding | None:
    patterns = [
        re.compile(r"exclusiv(?:idad|e)", re.I),
        re.compile(r"no\s+podr[aá]\s+(?:contratar|trabajar)\s+con", re.I),
    ]
    for pat in patterns:
        evidence = _match_evidence(clause.text, pat)
        if evidence:
            return RuleFinding(
                category=ClauseCategory.EXCLUSIVITY,
                risk_level=RiskLevel.MEDIUM,
                explanation="Posible cláusula de exclusividad detectada.",
                quoted_evidence=evidence,
                rule_name="exclusivity",
            )
    return None


RULES: list[RuleFn] = [
    rule_unlimited_liability,
    rule_liability_cap,
    rule_auto_renewal,
    rule_short_notice,
    rule_foreign_jurisdiction,
    rule_penalty,
    rule_exclusivity,
]


def apply_rules(clause: Clause) -> RuleFinding | None:
    """Return highest-severity rule finding for a clause."""
    findings: list[RuleFinding] = []
    for rule in RULES:
        result = rule(clause)
        if result:
            findings.append(result)
    if not findings:
        return None
    severity = {RiskLevel.HIGH: 3, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 1}
    return max(findings, key=lambda f: severity[f.risk_level])
