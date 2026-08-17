"""Analysis pipeline orchestration."""

from __future__ import annotations

from shield_engine.analysis.combiner import combine_findings
from shield_engine.analysis.llm.classifier import LlmClient, OpenAiClassifier
from shield_engine.analysis.rules.registry import apply_rules
from shield_engine.models import Clause, ClauseAnalysis, ContractRecord, ContractStatus, utcnow


def analyze_clauses(
    contract: ContractRecord,
    llm: LlmClient | None = None,
) -> list[ClauseAnalysis]:
    classifier = llm or OpenAiClassifier()
    analyses: list[ClauseAnalysis] = []
    for clause in contract.clauses:
        rule = apply_rules(clause)
        llm_result = classifier.classify(clause)
        analyses.append(combine_findings(clause.id, rule, llm_result))
    return analyses


def run_analysis(contract: ContractRecord, llm: LlmClient | None = None) -> ContractRecord:
    contract.status = ContractStatus.ANALYZING
    contract.analyses = analyze_clauses(contract, llm=llm)
    contract.status = ContractStatus.ANALYZED
    contract.updated_at = utcnow()
    return contract
