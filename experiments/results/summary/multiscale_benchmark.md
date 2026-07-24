| Backend | Movies | Intent | Iterations | Median (ms) | P95 (ms) |
|---|---:|---|---:|---:|---:|
| neo4j | 500 | movies_by_director | 100 | 10.252 | 16.953 |
| neo4j | 500 | common_movies | 100 | 15.156 | 22.406 |
| neo4j | 500 | movies_by_genre_rating | 100 | 5.229 | 7.082 |
| neo4j | 500 | directors_by_genre | 100 | 4.688 | 7.042 |
| sqlite | 500 | movies_by_director | 100 | 0.216 | 0.233 |
| sqlite | 500 | common_movies | 100 | 2.771 | 2.854 |
| sqlite | 500 | movies_by_genre_rating | 100 | 0.244 | 0.246 |
| sqlite | 500 | directors_by_genre | 100 | 0.574 | 0.909 |
| neo4j | 1000 | movies_by_director | 100 | 10.920 | 20.432 |
| neo4j | 1000 | common_movies | 100 | 16.902 | 23.112 |
| neo4j | 1000 | movies_by_genre_rating | 100 | 7.569 | 9.614 |
| neo4j | 1000 | directors_by_genre | 100 | 9.620 | 15.686 |
| sqlite | 1000 | movies_by_director | 100 | 0.571 | 0.828 |
| sqlite | 1000 | common_movies | 100 | 7.308 | 10.936 |
| sqlite | 1000 | movies_by_genre_rating | 100 | 0.530 | 0.881 |
| sqlite | 1000 | directors_by_genre | 100 | 1.329 | 1.887 |
| neo4j | 2000 | movies_by_director | 100 | 10.670 | 16.830 |
| neo4j | 2000 | common_movies | 100 | 25.666 | 37.530 |
| neo4j | 2000 | movies_by_genre_rating | 100 | 7.895 | 10.353 |
| neo4j | 2000 | directors_by_genre | 100 | 6.562 | 9.510 |
| sqlite | 2000 | movies_by_director | 100 | 1.063 | 1.424 |
| sqlite | 2000 | common_movies | 100 | 14.193 | 17.893 |
| sqlite | 2000 | movies_by_genre_rating | 100 | 1.068 | 1.888 |
| sqlite | 2000 | directors_by_genre | 100 | 3.145 | 4.861 |
| neo4j | 4999 | movies_by_director | 100 | 21.124 | 32.653 |
| neo4j | 4999 | common_movies | 100 | 44.312 | 52.081 |
| neo4j | 4999 | movies_by_genre_rating | 100 | 7.831 | 11.603 |
| neo4j | 4999 | directors_by_genre | 100 | 9.821 | 13.985 |
| sqlite | 4999 | movies_by_director | 100 | 3.062 | 5.093 |
| sqlite | 4999 | common_movies | 100 | 39.995 | 48.822 |
| sqlite | 4999 | movies_by_genre_rating | 100 | 2.177 | 2.414 |
| sqlite | 4999 | directors_by_genre | 100 | 5.940 | 6.802 |

Deterministic induced snapshots; same machine, warm-up and iteration policy.
