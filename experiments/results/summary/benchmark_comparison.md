| Intent | Iterations | Neo4j median (ms) | Neo4j p95 (ms) | SQLite median (ms) | SQLite p95 (ms) |
|---|---:|---:|---:|---:|---:|
| movies_by_director | 100 | 10.086 | 16.557 | 1.050 | 1.644 |
| common_movies | 100 | 38.324 | 48.326 | 12.041 | 13.070 |
| movies_by_genre_rating | 100 | 2.667 | 5.085 | 0.814 | 0.835 |
| directors_by_genre | 100 | 4.545 | 6.639 | 2.119 | 2.198 |

Controlled same-snapshot comparison; different execution models and no universal speed claim.
