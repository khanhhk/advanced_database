from src.qa.entity_linker import link
from src.processing.entity_resolution import resolve_entity


def test_entity_linker_exact_and_fuzzy():
    entities = [{"id": 1, "name": "Christopher Nolan", "type": "Person"}]
    assert link("Christopher Nolan", entities).confidence == 1
    assert link("Cristopher Nolan", entities).confidence >= .7
    assert link("unrelated", entities) is None


def test_entity_resolution_rejects_ambiguous_fuzzy_tie():
    left = {"id": "mention:1", "name": "Alex Kim"}
    candidates = [{"id": "p1", "name": "Alex Kim"}, {"id": "p2", "name": "Alex Kim"}]
    assert resolve_entity(left, candidates) is None
