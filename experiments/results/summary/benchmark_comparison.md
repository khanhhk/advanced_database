| Intent | Iterations | Neo4j median (ms) | Neo4j p95 (ms) | SQLite median (ms) | SQLite p95 (ms) |
|---|---:|---:|---:|---:|---:|
| movies_by_director | 100 | 16.230 | 23.676 | 1.056 | 1.663 |
| common_movies | 100 | 28.930 | 39.213 | 15.289 | 18.810 |
| movies_by_genre_rating | 100 | 10.061 | 15.842 | 1.000 | 1.498 |
| directors_by_genre | 100 | 7.986 | 13.238 | 2.651 | 3.701 |

Controlled same-snapshot comparison; different execution models and no universal speed claim.
