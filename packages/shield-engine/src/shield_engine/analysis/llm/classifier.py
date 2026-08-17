"""LLM-based clause classification with mandatory textual evidence."""

from __future__ import annotations

import json
import logging
from typing import Protocol

from openai import OpenAI

from shield_engine.config import settings
from shield_engine.models import Clause, ClauseCategory, LlmFinding, RiskLevel

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Eres un analista de riesgo contractual de D4TA Shield.
NO das veredictos de "firmar o no firmar". Señalas patrones de riesgo en cláusulas individuales.
Responde SOLO con JSON válido con estas claves:
- category: una de responsabilidad, indemnizacion, terminacion, renovacion, jurisdiccion, propiedad_intelectual, confidencialidad, no_competencia, exclusividad, penalizaciones, fuerza_mayor, otros
- risk_level: bajo, medio o alto
- explanation: breve, sin afirmar que el contrato es seguro
- quoted_evidence: cita textual EXACTA extraída de la cláusula que motiva la clasificación
- inconclusive: true si no puedes citar evidencia literal

Si no hay patrón de riesgo claro, usa risk_level bajo y quoted_evidence de la parte más relevante."""


class LlmClient(Protocol):
    def classify(self, clause: Clause) -> LlmFinding: ...


class OpenAiClassifier:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        key = api_key or settings.openai_api_key
        self.client = OpenAI(api_key=key) if key else None
        self.model = model or settings.llm_model

    def classify(self, clause: Clause) -> LlmFinding:
        if not self.client:
            return LlmFinding(
                category=ClauseCategory.OTHER,
                risk_level=RiskLevel.LOW,
                explanation="LLM no configurado — clasificación omitida.",
                quoted_evidence=clause.text[:200],
                inconclusive=True,
            )

        user_msg = f"Título: {clause.title}\n\nCláusula:\n{clause.text[:6000]}"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=settings.llm_temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
            )
            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)
        except Exception as exc:
            logger.warning("LLM classification failed: %s", exc)
            return LlmFinding(
                category=ClauseCategory.OTHER,
                risk_level=RiskLevel.LOW,
                explanation=f"Error en clasificación LLM: {exc}",
                quoted_evidence=clause.text[:120],
                inconclusive=True,
            )

        category = _parse_category(data.get("category", "otros"))
        risk = _parse_risk(data.get("risk_level", "bajo"))
        evidence = str(data.get("quoted_evidence", "")).strip()
        inconclusive = bool(data.get("inconclusive", False)) or not evidence
        if evidence and evidence not in clause.text:
            inconclusive = True
            evidence = clause.text[: min(200, len(clause.text))]

        return LlmFinding(
            category=category,
            risk_level=risk,
            explanation=str(data.get("explanation", "")).strip() or "Sin explicación.",
            quoted_evidence=evidence or clause.text[:120],
            inconclusive=inconclusive,
        )


def _parse_category(value: str) -> ClauseCategory:
    mapping = {c.value: c for c in ClauseCategory}
    return mapping.get(str(value).lower().strip(), ClauseCategory.OTHER)


def _parse_risk(value: str) -> RiskLevel:
    mapping = {r.value: r for r in RiskLevel}
    return mapping.get(str(value).lower().strip(), RiskLevel.LOW)
