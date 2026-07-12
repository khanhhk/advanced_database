from src.qa.entity_linker import link


def test_entity_linker_exact_and_fuzzy():
    entities = [{"id": 1, "name": "Christopher Nolan", "type": "Person"}]
    assert link("Christopher Nolan", entities).confidence == 1
    assert link("Cristopher Nolan", entities).confidence >= .7
    assert link("unrelated", entities) is None

