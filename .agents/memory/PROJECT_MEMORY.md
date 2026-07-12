# Movie Knowledge Graph — project memory

Last reviewed: 2026-07-12. This briefing summarizes all 5 PPTX files, the DOCX
brief, and all 6 Markdown files currently present (the request mentioned 5 MD
files, but the repository contains `README.md` plus 5 under `docs/`).

## Mission and thesis

Build an end-to-end Knowledge Graph for the movie domain that demonstrates why
graphs are natural for heterogeneous, highly connected and multi-hop data. The
system integrates movie data, models explicit semantics, supports traversal and
rule-based inference, and exposes two explainable applications: question
answering and movie recommendation.

Research question: how can a Knowledge Graph integrate multi-source movie data,
support multi-hop querying and inference, and provide more explainable answers
and recommendations than conventional data models?

## Agreed scope

- Target dataset: 2,000–5,000 movies; a small committed seed supports offline demos.
- Core nodes: `Movie`, `Person`, `Genre`, `Keyword`, `Studio`.
- Core edges: `ACTED_IN`, `DIRECTED`, `HAS_GENRE`, `HAS_KEYWORD`, `PRODUCED_BY`.
- Derived edge: `CO_STARRED_WITH` with evidence/count and `derived: true`.
- `Award`/`WON`, Wikidata, NLP over overview text, LLM-to-Cypher, vector search,
  GraphRAG and embeddings are extensions, not MVP requirements.
- Use one `Person` label; roles are expressed by relationships because a person
  may be both actor and director.

## Architecture and technology choices

Data flow: TMDB API + IMDb datasets → immutable cached raw JSON/TSV → cleaning
and validation → entity resolution → normalized node/edge tables → Neo4j. A
subset is exported as RDF/Turtle for OWL/SPARQL comparison.

- Python 3.11, FastAPI/Pydantic, pytest.
- Neo4j 5/property graph/Cypher is the operational store because traversal and
  implementation are straightforward.
- RDF/RDFS/OWL, RDFLib and Protégé/Jena illustrate standards, semantic
  constraints, SPARQL and reasoner capabilities.
- Stable source IDs are keys. Match TMDB↔IMDb by exact IDs first; fuzzy matching
  is a logged, confidence-scored fallback, never a name-based primary key.
- Import nodes before edges, create constraints/indexes first, use parameterized
  Cypher, transactions and `MERGE`; repeated imports must be idempotent.
- Every asserted or derived fact should be traceable to a source or derivation.

## Domain model

Important properties include `Movie(tmdb_id, imdb_id, title, release_date,
runtime, rating, imdb_rating, imdb_votes, popularity, overview)`, `Person(tmdb_id, imdb_id, name,
birthday)`, `Genre(genre_id, name)`, `Keyword(keyword_id, name)`, and
`Studio(company_id, name, country)`. `ACTED_IN` carries `character` and
`cast_order`.

Competency questions cover movies by director; cast of a movie; co-stars and
shared movies; genre/rating conditions; director–genre patterns; shortest paths
between people; frequent collaborator pairs; and similar/top-N movies with an
explanation. Maintain at least 10 Cypher queries, including 4–5 multi-hop ones,
plus representative SPARQL equivalents.

## Applications

`POST /ask` follows: intent detection → slot extraction → entity linking → a
whitelisted parameterized Cypher template → answer plus evidence. The current
project advertises 8 intents. Never concatenate user input into Cypher.

`POST /recommend` ranks graph-neighbor movies and returns shared metadata as an
explanation. Starting weighted overlap is approximately director 3.0, actor
2.0, genre 1.5, keyword 1.0; weighted Jaccard should also be evaluated to avoid
bias toward movies with large casts. Supporting endpoints are `/health`,
`/stats`, and `/entities/search`.

Implemented backend boundary (updated 2026-07-12): the application runs only
against real TMDB data imported into Neo4j. There is no runtime seed fallback;
small deterministic data exists only under `tests/fixtures`. Neo4j executes QA
through the fixed parameterized Cypher catalog and computes recommendation
similarity in the database. TMDB collection supports `--count 2000..5000`, using
immutable page/movie caches. Synthetic memory benchmarks must be labeled with
backend and movie count and must not be reported as Neo4j performance.

IMDb integration (updated 2026-07-12) is deliberately storage-bounded: TMDB
remains the graph source, while only compressed `title.ratings.tsv.gz` is
downloaded. The pipeline streams it without extraction, exact-joins the small
set of TMDB `imdb_id` values, and stores `imdb_rating`/`imdb_votes` separately
from TMDB `rating`. It never loads complete IMDb data into memory or Neo4j.
Checksums and match counts are recorded for provenance; ignored raw IMDb data
may be deleted after processing.

TMDB collection now preserves source IDs and credit metadata instead of reducing
credits to names. Processed people prefer `person_id=tmdb:<id>`, with legacy
name hashes accepted only for old fixtures/raw caches; `ACTED_IN` retains
character and cast order. Genre, keyword, and studio source IDs are preserved as
well. QA entity slots are linked to canonical Movie/Person entities before
parameterized Cypher execution, and link confidence is returned as evidence.
Deterministic silver corpora cover 100 entity-resolution cases (75 positive/25
negative), 50 evidence-backed co-star facts, and 20 recommendation cases with
an explicit relevance rubric. Their metrics may be reported only as silver
evaluation until an independent reviewer and adjudication are recorded.

## Quality and evaluation

Measure entity-resolution precision/recall/F1 on about 100 labeled pairs; data
missing/duplicate/invalid-edge rates; constraint violations and orphan nodes;
median/p95 query latency at multiple scales; precision on about 50 inferred
facts; QA accuracy on 20–30 questions; recommendation relevance (Precision@K,
NDCG@K or documented manual review); and the fraction of recommendations with
an evidence path. Store configurations and CSV/JSON results so experiments are
reproducible.

Current reproducible evidence (2026-07-12): the corpus has 2,000 movies and the
loaded graph validates at 36,574 nodes/337,822 relationships with zero structural
violations. Exact IMDb ratings match 1,677 of 1,785 movies carrying an IMDb ID.
Silver entity-resolution P/R/F1 is 1.00; silver co-star precision is 1.00;
recommendation P@10 is 0.64, NDCG@10 is 0.699, and explanation coverage is 1.00.
The real Neo4j benchmark uses Neo4j 5.26.28, one warm-up and 100 iterations per
question at 2,000 movies; intent medians range 2.34–110.65 ms and p95 ranges
3.83–126.20 ms. This single-scale result is not a scalability claim.

## Source synthesis

The original Office documents are archived under `docs/sources/` and remain the
authoritative full-fidelity sources for report/slide reconstruction.

- `docs/sources/KnowledgeGraph_KhungNoiDung_ChiTiet.docx`: authoritative assignment framing,
  full lifecycle, ontology, ETL/entity resolution, Neo4j/RDF comparison,
  reasoning, integrated QA/recommendation, evaluation, risks and extensions.
- `docs/sources/KnowledgeGraph_50slide_VN - Repaired.pptx`: Vietnamese 50-slide presentation
  of the project narrative, from motivation and foundations through design,
  construction, query/reasoning, applications, evaluation and roadmap.
- `docs/sources/Knowledge_Graph_AI_Agent_50slides.pptx`: connects Knowledge Graphs to AI
  agents—grounding, retrieval, planning/reasoning, tool use, memory,
  explainability and GraphRAG-style extensions. This is conceptual context, not
  permission to expand the MVP automatically.
- `docs/sources/Co-so-du-lieu-do-thi-Graph-Database.pptx`: graph-database foundations:
  property graphs, nodes/edges/properties, graph-vs-relational trade-offs,
  Neo4j/Cypher modeling and traversal/query patterns.
- `docs/sources/8_Biểu diễn tri thức.pptx` (84 slides): course foundations spanning the
  data–information–knowledge hierarchy, production rules, forward/backward
  inference and conflict resolution, frames/inheritance, semantic networks and
  ontology-oriented knowledge representation.
- `docs/sources/Ontology_va_Ung_dung.pptx`: ontology fundamentals; class/property/individual,
  taxonomy versus ontology, RDF/RDFS/OWL/SPARQL, Protégé and reasoners, semantic
  web/linked data and applications in search, health, commerce, AI, recommenders,
  IoT and enterprise knowledge graphs.
- `docs/PROJECT_PLAN.md`: canonical project scope, model, architecture, work
  packages, nine-week schedule, demo, evaluation, risks and deliverables.
- `docs/CODE_PLAN.md`: repository layout, implementation order, API/query/test
  requirements and engineering quality rules.
- `docs/REPORT_OUTLINE.md` and `docs/SLIDE_OUTLINE.md`: expected report and
  presentation story; keep final artifacts aligned with measured evidence.
- Root `README.md`: current runnable interface and commands; prefer it over old
  planning prose when describing implemented behavior.
- `docs/README.md`: index and precedence guidance for the planning documents.

## Working rules and precedence

For facts about what runs today: source code/tests/configuration, then root
`README.md`. For intended scope and academic deliverables: `PROJECT_PLAN.md`,
the DOCX brief, then report/slide outlines. The lecture decks explain theory and
motivation; they do not override repository behavior.

Keep raw external data and secrets out of Git. Preserve immutable raw inputs,
checksums/manifests for processed outputs, demo independence from network APIs,
and the ability to reproduce tests and experiments from documented commands.
