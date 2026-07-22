| Backend | Movies | Intent | Iterations | Median (ms) | P95 (ms) |
|---|---:|---|---:|---:|---:|
| neo4j | 500 | movies_by_director | 100 | 9.885 | 17.886 |
| neo4j | 500 | common_movies | 100 | 12.627 | 17.420 |
| neo4j | 500 | movies_by_genre_rating | 100 | 4.696 | 8.403 |
| neo4j | 500 | directors_by_genre | 100 | 5.289 | 7.324 |
| sqlite | 500 | movies_by_director | 100 | 0.216 | 0.325 |
| sqlite | 500 | common_movies | 100 | 2.756 | 2.892 |
| sqlite | 500 | movies_by_genre_rating | 100 | 0.212 | 0.239 |
| sqlite | 500 | directors_by_genre | 100 | 0.504 | 0.559 |
| neo4j | 1000 | movies_by_director | 100 | 6.019 | 7.650 |
| neo4j | 1000 | common_movies | 100 | 14.991 | 20.369 |
| neo4j | 1000 | movies_by_genre_rating | 100 | 5.933 | 7.614 |
| neo4j | 1000 | directors_by_genre | 100 | 5.804 | 7.983 |
| sqlite | 1000 | movies_by_director | 100 | 0.475 | 0.496 |
| sqlite | 1000 | common_movies | 100 | 5.252 | 5.870 |
| sqlite | 1000 | movies_by_genre_rating | 100 | 0.450 | 0.488 |
| sqlite | 1000 | directors_by_genre | 100 | 1.195 | 1.236 |
| neo4j | 2000 | movies_by_director | 100 | 9.442 | 14.276 |
| neo4j | 2000 | common_movies | 100 | 23.473 | 31.311 |
| neo4j | 2000 | movies_by_genre_rating | 100 | 4.840 | 12.596 |
| neo4j | 2000 | directors_by_genre | 100 | 6.933 | 10.633 |
| sqlite | 2000 | movies_by_director | 100 | 1.072 | 1.440 |
| sqlite | 2000 | common_movies | 100 | 12.652 | 13.426 |
| sqlite | 2000 | movies_by_genre_rating | 100 | 0.916 | 0.936 |
| sqlite | 2000 | directors_by_genre | 100 | 2.424 | 2.485 |

Deterministic induced snapshots; same machine, warm-up and iteration policy.
