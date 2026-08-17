"""Combine rule and LLM findings; flag discrepancies for priority review."""

from __future__ import annotations

from shield_engine.models import (
    ClauseAnalysis,
    DetectionLayer,
    LlmFinding,
    RiskLevel,
    RuleFinding,
)

SEVERITY = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3}


def _severity_gap(a: RiskLevel, b: RiskLevel) -> int:
    return abs(SEVERITY[a] - SEVERITY[b])


def combine_findings(
    clause_id: str,
    rule: RuleFinding | None,
    llm: LlmFinding | None,
) -> ClauseAnalysis:
    """Merge layers; never silently resolve disagreements."""
    if rule and llm and not llm.inconclusive:
        gap = _severity_gap(rule.risk_level, llm.risk_level)
        category_mismatch = rule.category != llm.category
        requires_review = gap >= 2 or (category_mismatch and SEVERITY[rule.risk_level] >= 2)

        if requires_review:
            final_risk = max(rule.risk_level, llm.risk_level, key=lambda r: SEVERITY[r])
            reason_parts = []
            if gap >= 2:
                reason_parts.append(
                    f"Discrepancia de severidad: regla={rule.risk_level.value}, LLM={llm.risk_level.value}"
                )
            if category_mismatch:
                reason_parts.append(
                    f"Discrepancia de categoría: regla={rule.category.value}, LLM={llm.category.value}"
                )
            return ClauseAnalysis(
                clause_id=clause_id,
                category=rule.category if SEVERITY[rule.risk_level] >= SEVERITY[llm.risk_level] else llm.category,
                risk_level=final_risk,
                explanation=f"{rule.explanation} | LLM: {llm.explanation}",
                quoted_evidence=rule.quoted_evidence or llm.quoted_evidence,
                detected_by=DetectionLayer.BOTH,
                requires_priority_review=True,
                rule_finding=rule,
                llm_finding=llm,
                discrepancy_reason="; ".join(reason_parts),
            )

        return ClauseAnalysis(
            clause_id=clause_id,
            category=rule.category,
            risk_level=rule.risk_level,
            explanation=rule.explanation,
            quoted_evidence=rule.quoted_evidence,
            detected_by=DetectionLayer.BOTH,
            requires_priority_review=False,
            rule_finding=rule,
            llm_finding=llm,
        )

    if rule:
        return ClauseAnalysis(
            clause_id=clause_id,
            category=rule.category,
            risk_level=rule.risk_level,
            explanation=rule.explanation,
            quoted_evidence=rule.quoted_evidence,
            detected_by=DetectionLayer.RULE,
            requires_priority_review=False,
            rule_finding=rule,
            llm_finding=llm,
        )

    if llm:
        return ClauseAnalysis(
            clause_id=clause_id,
            category=llm.category,
            risk_level=llm.risk_level,
            explanation=llm.explanation,
            quoted_evidence=llm.quoted_evidence,
            detected_by=DetectionLayer.LLM,
            requires_priority_review=llm.inconclusive,
            rule_finding=None,
            llm_finding=llm,
            discrepancy_reason="Evidencia LLM inconclusa" if llm.inconclusive else None,
        )

    from shield_engine.models import ClauseCategory

    return ClauseAnalysis(
        clause_id=clause_id,
        category=ClauseCategory.OTHER,
        risk_level=RiskLevel.LOW,
        explanation="No se detectaron patrones de riesgo significativos.",
        quoted_evidence="",
        detected_by=DetectionLayer.LLM,
        requires_priority_review=False,
    )
