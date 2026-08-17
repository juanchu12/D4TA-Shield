from shield_engine.analysis.rules.registry import apply_rules


def test_unlimited_liability_detected(liability_clause):
    finding = apply_rules(liability_clause)
    assert finding is not None
    assert finding.risk_level.value == "alto"
    assert "sin límite" in finding.quoted_evidence.lower()


def test_no_rule_on_benign_text():
    from shield_engine.models import Clause, ClausePosition, new_id

    clause = Clause(
        id=new_id(),
        contract_id="c1",
        index=0,
        title="Objeto",
        text="Las partes acuerdan colaborar de buena fe en el marco del contrato.",
        position=ClausePosition(page=1, char_start=0, char_end=80),
    )
    assert apply_rules(clause) is None
