| Intent | Iterations | Neo4j median (ms) | Neo4j p95 (ms) | SQLite median (ms) | SQLite p95 (ms) |
|---|---:|---:|---:|---:|---:|
| movies_by_director | 100 | 20.922 | 31.057 | 3.207 | 3.572 |
| common_movies | 100 | 45.249 | 53.083 | 37.488 | 40.155 |
| movies_by_genre_rating | 100 | 6.717 | 9.016 | 2.180 | 2.295 |
| directors_by_genre | 100 | 7.763 | 10.593 | 5.925 | 6.340 |

Controlled same-snapshot comparison; different execution models and no universal speed claim.
