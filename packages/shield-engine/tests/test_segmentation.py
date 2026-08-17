from shield_engine.segmentation.clause_parser import segment_clauses


def test_segments_multiple_clauses(synthetic_text):
    clauses = segment_clauses("contract-1", synthetic_text)
    assert len(clauses) >= 3
    titles = [c.title for c in clauses]
    assert any("RESPONSABILIDAD" in t for t in titles)
    assert all(c.text for c in clauses)
    assert all(c.position.char_end > c.position.char_start for c in clauses)
