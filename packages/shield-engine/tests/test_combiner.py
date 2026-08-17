from shield_engine.analysis.combiner import combine_findings
from shield_engine.analysis.rules.registry import apply_rules
from shield_engine.models import DetectionLayer, RiskLevel


def test_agreement_no_discrepancy(liability_clause, mock_llm_high):
    rule = apply_rules(liability_clause)
    result = combine_findings(liability_clause.id, rule, mock_llm_high)
    assert result.detected_by == DetectionLayer.BOTH
    assert result.requires_priority_review is False
    assert result.risk_level == RiskLevel.HIGH


def test_discrepancy_flags_priority_review(liability_clause, mock_llm_low):
    rule = apply_rules(liability_clause)
    result = combine_findings(liability_clause.id, rule, mock_llm_low)
    assert result.requires_priority_review is True
    assert result.discrepancy_reason is not None
    assert "Discrepancia" in result.discrepancy_reason
