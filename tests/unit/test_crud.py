from src.kg import crud


class Repository:
    def __init__(self): self.calls = []
    def run(self, query, **parameters):
        self.calls.append((query, parameters))
        if query == crud.DELETE_MOVIE: return [{"deleted": 1}]
        if query == crud.READ_MOVIE: return [{"movie": {"tmdb_id": parameters["tmdb_id"]}, "actors": [], "directors": [], "genres": []}]
        return [{"movie": parameters, "relationship": "ACTED_IN"}]


def test_crud_uses_parameters_and_explicit_queries():
    repository = Repository()
    assert crud.create_movie(repository, tmdb_id=1, title="A")["title"] == "A"
    assert crud.read_movie(repository, 1)["movie"]["tmdb_id"] == 1
    assert crud.update_movie(repository, tmdb_id=1, overview="x", runtime=90)["overview"] == "x"
    assert crud.upsert_cast(repository, person_id="p1", tmdb_id=1, character="X", cast_order=0)
    assert crud.delete_movie(repository, 1)
    assert all("$" in query and parameters for query, parameters in repository.calls)
