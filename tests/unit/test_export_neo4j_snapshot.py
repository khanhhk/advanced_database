import json

from experiments.export_neo4j_snapshot import export


class Repository:
    def run(self, query):
        if "m{.*}" in query: return [{"movie": {"tmdb_id": 1, "title": "A"}}]
        if "ACTED_IN" in query: return [{"movie_id": 1, "source_id": 10, "name": "Actor", "character": "A", "cast_order": 0}]
        if "DIRECTED" in query: return [{"movie_id": 1, "source_id": 11, "name": "Director"}]
        return []


def test_exports_raw_compatible_snapshot(tmp_path):
    output = tmp_path / "snapshot.json"; counts = export(Repository(), output)
    movie = json.loads(output.read_text())["movies"][0]
    assert counts["movies"] == 1 and movie["actors"][0]["tmdb_id"] == 10
    assert movie["directors"][0]["name"] == "Director"
