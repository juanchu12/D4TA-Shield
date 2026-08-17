"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from shield_engine.models import Clause, ClauseCategory, ClausePosition, LlmFinding, RiskLevel, new_id
from shield_engine.store.sqlite import ContractStore


SYNTHETIC_CONTRACT = """
CLÁUSULA PRIMERA — OBJETO
El presente contrato regula la prestación de servicios de consultoría entre las partes.

CLÁUSULA SEGUNDA — RESPONSABILIDAD
La responsabilidad del proveedor será sin límite de responsabilidad por daños indirectos
y lucro cesante derivados del incumplimiento.

CLÁUSULA TERCERA — RENOVACIÓN
El contrato se prorrogará automáticamente por periodos anuales salvo preaviso de 10 días.

CLÁUSULA CUARTA — JURISDICCIÓN
Las partes se someten a la jurisdicción de los tribunales de Delaware.
"""


@pytest.fixture
def synthetic_text() -> str:
    return SYNTHETIC_CONTRACT.strip()


@pytest.fixture
def liability_clause() -> Clause:
    return Clause(
        id=new_id(),
        contract_id="test-contract",
        index=1,
        title="CLÁUSULA SEGUNDA — RESPONSABILIDAD",
        text=(
            "La responsabilidad del proveedor será sin límite de responsabilidad "
            "por daños indirectos y lucro cesante."
        ),
        position=ClausePosition(page=1, char_start=100, char_end=250),
    )


@pytest.fixture
def mock_llm_high() -> LlmFinding:
    return LlmFinding(
        category=ClauseCategory.LIABILITY,
        risk_level=RiskLevel.HIGH,
        explanation="Responsabilidad amplia sin cap.",
        quoted_evidence="sin límite de responsabilidad",
    )


@pytest.fixture
def mock_llm_low() -> LlmFinding:
    return LlmFinding(
        category=ClauseCategory.LIABILITY,
        risk_level=RiskLevel.LOW,
        explanation="Cláusula estándar.",
        quoted_evidence="responsabilidad del proveedor",
    )


@pytest.fixture
def memory_store(tmp_path) -> ContractStore:
    return ContractStore(db_path=tmp_path / "test.db")
