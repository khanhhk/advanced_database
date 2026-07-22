| Backend | Movies | Intent | Iterations | Median (ms) | P95 (ms) |
|---|---:|---|---:|---:|---:|
| neo4j | 500 | movies_by_director | 100 | 3.741 | 6.325 |
| neo4j | 500 | common_movies | 100 | 7.822 | 8.688 |
| neo4j | 500 | movies_by_genre_rating | 100 | 1.970 | 2.773 |
| neo4j | 500 | directors_by_genre | 100 | 3.065 | 4.662 |
| sqlite | 500 | movies_by_director | 100 | 0.220 | 0.334 |
| sqlite | 500 | common_movies | 100 | 2.712 | 2.967 |
| sqlite | 500 | movies_by_genre_rating | 100 | 0.241 | 0.246 |
| sqlite | 500 | directors_by_genre | 100 | 0.561 | 0.575 |
| neo4j | 1000 | movies_by_director | 100 | 6.546 | 11.395 |
| neo4j | 1000 | common_movies | 100 | 12.196 | 15.175 |
| neo4j | 1000 | movies_by_genre_rating | 100 | 3.457 | 5.024 |
| neo4j | 1000 | directors_by_genre | 100 | 3.978 | 6.514 |
| sqlite | 1000 | movies_by_director | 100 | 0.500 | 0.833 |
| sqlite | 1000 | common_movies | 100 | 5.968 | 6.664 |
| sqlite | 1000 | movies_by_genre_rating | 100 | 0.470 | 0.475 |
| sqlite | 1000 | directors_by_genre | 100 | 1.214 | 1.468 |
| neo4j | 2000 | movies_by_director | 100 | 10.735 | 15.612 |
| neo4j | 2000 | common_movies | 100 | 19.528 | 25.232 |
| neo4j | 2000 | movies_by_genre_rating | 100 | 3.496 | 4.513 |
| neo4j | 2000 | directors_by_genre | 100 | 5.545 | 7.537 |
| sqlite | 2000 | movies_by_director | 100 | 1.092 | 1.667 |
| sqlite | 2000 | common_movies | 100 | 13.094 | 14.242 |
| sqlite | 2000 | movies_by_genre_rating | 100 | 0.836 | 0.931 |
| sqlite | 2000 | directors_by_genre | 100 | 2.220 | 2.454 |

Deterministic induced snapshots; same machine, warm-up and iteration policy.
