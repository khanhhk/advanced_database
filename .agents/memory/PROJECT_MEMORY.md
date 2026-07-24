# Movie Knowledge Graph — project memory

Last reviewed: 2026-07-22. This briefing summarizes the original Office sources,
the project Markdown documents and the current implementation artifacts.

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
- RDF/RDFS/OWL, RDFLib and Apache Jena/Fuseki illustrate standards, semantic
  constraints, SPARQL and reasoner capabilities.
- The standards path is executable: RDFLib materializes the declared RDFS/OWL-RL
  subset (domain/range, inverse and symmetric properties) and validates functional
  properties, disjoint classes and required Movie titles. It reports before/after
  triple counts and violations. A separate Apache Jena Fuseki 6.1.0 Docker profile
  loads the full RDF snapshot through an assembler-backed GenericRuleReasoner in
  forward mode and executes the ten-query SPARQL catalog. Both paths deliberately
  implement the same declared subset and are not presented as full OWL 2 DL.
  Its isolated runtime configuration lives under `experiments/semantic/jena/` because Jena
  is an evaluation engine, not part of the application's production path.
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

`POST /ask` optionally uses a configured LLM only as a constrained question
planner: natural language → validated `QueryPlan` JSON → entity linking → a
whitelist Cypher compiler → answer plus graph evidence. The LLM never writes
Cypher or answers from its own knowledge. Without LLM configuration, the current
9-intent deterministic parser remains the runtime fallback, including
role-agnostic lookup of movies associated with a person. Never concatenate user
input into Cypher.

Local planner runtime (updated 2026-07-13): `Qwen/Qwen3-8B-AWQ` is served by
vLLM 0.25.0 on an RTX 3060 12 GB at `127.0.0.1:8001`. It uses a 4,096-token
context, 0.85 GPU-memory utilization and native sampling via
`VLLM_USE_FLASHINFER_SAMPLER=0`, avoiding a system CUDA toolkit/nvcc dependency.
The isolated `.venv-llm` is prepared with `make llm-setup`; `make llm-run`
starts the server. Pydantic JSON Schema is passed as constrained output, and
`/no_think` keeps the planner concise.

`POST /recommend` uses one explainable IDF-weighted graph similarity ranker. A
shared feature contributes `type_weight * (1 + ln((N+1)/(df+1)))`, so common
features are discounted and rare director, actor, keyword, genre, or studio
connections contribute more. Supporting endpoints are `/health`, `/stats`, and
`/entities/search`.
The web UI is a two-tab interface: persistent multi-turn-style QA history
(each turn remains stateless at the backend) and explainable recommendation.
Forms use explicit DOM selectors/listeners rather
than browser-generated ID globals; responses render as messages/cards with
human labels instead of raw JSON. Recommendation uses movie-title autocomplete
with release year for disambiguation; the selected TMDB ID remains internal.
There is no end-user ranking-method selector.

Implemented backend boundary (updated 2026-07-12): the application runs only
against real TMDB data imported into Neo4j. There is no runtime seed fallback;
small deterministic data exists only under `tests/fixtures`. Neo4j executes QA
through the fixed parameterized Cypher catalog and computes recommendation
similarity in the database. TMDB collection supports `--count 2000..5000`, using
immutable page/movie caches. Evaluation and benchmark claims use production
Neo4j; the former synthetic memory benchmark was removed to keep one
authoritative performance path.

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
Full-text entity candidates now precede fuzzy reranking. Linked entities retain
their stable `tmdb_id`/source-qualified ID through deterministic catalog and LLM
compiler execution; canonical-name equality is only a fallback for legacy
fixtures without IDs. This prevents substring contamination such as querying
`The Dark Knight` and also matching `The Dark Knight Rises`, and prevents query
execution from expanding to every same-name entity after one candidate is linked.
The nine known intents remain fixed parameterized Cypher templates; unrestricted
LLM-to-Cypher is deliberately not enabled.
Deterministic silver corpora cover 100 entity-resolution cases (75 positive/25
negative), 50 evidence-backed co-star facts, and 20 recommendation cases with
an explicit relevance rubric. Entity candidates now use the four nearest
same-type names, creating meaningful hard negatives and conservative abstention
cases. Metrics are explicitly limited to the declared case-generation protocol,
rubric and snapshot and are not generalized as production accuracy.

## Quality and evaluation

Measure entity-resolution precision/recall/F1 on about 100 labeled pairs; data
missing/duplicate/invalid-edge rates; constraint violations and orphan nodes;
median/p95 query latency at multiple scales; precision on about 50 inferred
facts; QA accuracy on 20–30 questions; recommendation relevance (Precision@K,
NDCG@K or documented manual review); and the fraction of recommendations with
an evidence path. Store configurations and CSV/JSON results so experiments are
reproducible.
The evaluation workflow also provides a same-snapshot SQLite baseline for four
representative relational queries and deterministic induced snapshots at
500/1,000/2,000/4,999 Movie. Each scale is authoritatively loaded into the isolated
Neo4j test service and built in SQLite from the same filtered CSV set. The workflow
generates CSV/Markdown/SVG evidence summaries.
Neo4j/SQLite comparisons are valid only when run on the same machine, dataset,
warm-up policy and iteration count.
The RDF workflow parses and executes all ten numbered SPARQL queries after
materialization. Administrative Movie CRUD is parameterized and tested but is
not exposed through the public API. Integration tests use a dedicated temporary
Neo4j service on Bolt 7688, so they can verify reset/import/idempotency, QA,
recommendation and CRUD without touching the demo graph.
The root `Makefile` is intentionally limited to demo, setup, test and optional
LLM operations. Reproducible research workflows are organized as Python modules
under `experiments/{corpora,evaluation,benchmarks,semantic,reporting}`; measured
artifacts are grouped under matching `experiments/results/` subdirectories.
Every experiments subdirectory has a README describing its purpose, input,
output, dependencies and safety limits. Docker Compose commands remain explicit.

Current reproducible evidence (full rerun 2026-07-24): the pipeline receives
5,000 records and retains 4,999 valid movies; one orphan movie with no graph
relationships is rejected. The loaded graph validates at 76,612 nodes/846,309
relationships with zero structural violations. Exact IMDb ratings match 4,351
of 4,558 movies carrying an IMDb ID.
The final repository gate passes 37/37 tests, compileall and all tracked source
checksums.
The full-snapshot knowledge-quality audit has zero stable-ID duplicates,
conflicting required values, missing required fields, invalid foreign keys and
duplicate endpoint pairs, plus 100% provenance coverage for rows carrying a
source field. Two repeated TMDB actor credits are collapsed by combining
characters and retaining the smallest cast order. Two hundred nine duplicate Person
names remain separate because names are not identity keys.
On the nearest-name hard-negative silver ER corpus, precision is 1.000, recall
0.933 and F1 0.966 (TP=70, TN=25, FP=0, FN=5); four misses are conservative
short-name typo abstentions and one is a tied same-title Movie abstention. Silver
co-star precision is 1.00;
the strengthened 20-question Neo4j QA smoke corpus passes 20/20 with evidence,
including a negative assertion that `The Dark Knight` cast lookup excludes actors
linked only to `The Dark Knight Rises`; semantic
materialization adds 86,509 triples (342,683 to 429,192) with zero violations.
Jena evaluates the ontology+data union (342,753 to 429,262), exposes 81,030 inverse
`hasActor` triples and executes all ten SPARQL queries successfully.
The controlled Neo4j/SQLite benchmark uses one warm-up and 100 iterations for four
equivalent queries on 500/1,000/2,000/4,999 Movie induced snapshots. SQLite is faster on
all measured query/scale pairs. The four-scale trend supports a trade-off and
growth discussion, but is not a universal engine ranking or a scalability claim
because concurrency, cold cache, resources and larger datasets are not measured.
On 20 silver cases against real Neo4j, the
IDF-weighted production ranker reaches P@10 0.635 and NDCG@10 0.672. Historical
results were overlap 0.67/0.723, weighted Jaccard 0.64/0.699, and hybrid
0.59/0.657; these remain design history rather than end-user alternatives.
Runtime preparation is idempotent: dependency stamps follow `pyproject.toml`,
while a SHA-256 over all processed node/edge CSV files plus the live Movie count
decides whether import is required. This detects transformation changes even when
the raw source checksum and Movie count stay constant. Normal `make demo` reuses
the graph when that processed checksum matches.

## Source synthesis

The large Office lecture/source files used during initial synthesis are not
stored in the demo repository. Current source code, configuration, Markdown
documents and committed experiment artifacts are the verifiable project sources.
- `docs/technical/implementation-plan.md`: repository layout, implementation order, API/query/test
  requirements and engineering quality rules.
- `docs/deliverables/report/outline.md` and
  `docs/deliverables/defense/slide-outline.md`: expected report and
  presentation story; keep final artifacts aligned with measured evidence.
- `docs/deliverables/report/draft.md`: supporting Vietnamese manuscript snapshot. The
  authoritative submission source is edited directly under `report_latex/` and
  is organized into six content chapters aligned with the applicable
  report-content criteria in `ChecklistCSDLNCv2.XLS`, followed by a conclusion
  chapter. Rubric items for report quality, presentation and oral defense remain
  assessment criteria rather than self-describing report sections,
  including theory, related work, implementation, measured evidence, validity
  limits, numeric IEEE-style references and reproducibility appendices. Its
  front matter, evaluation prose and measured values were finalized against the
  2026-07-22 evidence run.
- `report_latex/`: self-contained, submission-oriented LaTeX source for manual
  upload to Overleaf.
  `main.tex` assembles the six content chapters, conclusion and appendices;
  `ref.bib` is the normalized
  bibliography, and all 14 image calls resolve to vector PDF assets under
  `report_latex/images/`. Eleven editable diagram sources live in
  `report_latex/images/sources/*.drawio`; three measured charts reflect the
  committed experiment CSV/JSON. `web_ui.pdf` is explicitly a
  source-aligned wireframe and may later be replaced by a real screenshot with
  the same filename. Edit `contents/*.tex` directly and select pdfLaTeX on
  Overleaf. Final report PDF and automatic report-generation scripts are not
  stored in the repository.
- `docs/deliverables/checklist-traceability.md`: one-to-one mapping of all 20 N5 rubric
  criteria to report sections, source files and measured artifacts. Criteria 19
  and 20 remain human performance gates even though their preparation artifacts
  are complete.
- Slide PDF/PPTX and automatic slide-generation scripts are not stored. Use
  `docs/deliverables/defense/slide-outline.md` and the defense materials to
  prepare slides manually.
- `docs/deliverables/defense/defense-script.md` and
  `docs/deliverables/defense/defense-qa.md`: timed presentation/demo
  sequence, fallback plan, rehearsal gate and 25 evidence-backed oral-defense
  questions. A rehearsal result must never be claimed until a human completes it.
- Root `README.md`: current runnable interface and commands; prefer it over old
  planning prose when describing implemented behavior.
- `docs/README.md`: top-level index and precedence guidance. Documentation is
  grouped into `technical/`, `runbooks/`, and `deliverables/`; every subdirectory
  has a local README.
- `docs/technical/architecture-flow.drawio`: editable current-architecture flow.
- `docs/technical/architecture.md`: block-by-block and request-path explanation
  of the draw.io architecture.
- `docs/runbooks/qwen-vllm.md`: reproducible GPU/vLLM/Qwen setup and
  troubleshooting runbook.
- `docs/runbooks/dbeaver-neo4j.md`: reproducible DBeaver Community demo runbook. It
  configures the official Neo4j JDBC full bundle as a custom Generic driver,
  documents SQL-to-Cypher versus native Cypher use, and covers connection and
  authentication troubleshooting for the local Compose graph.
- `docs/runbooks/demo.md`: the presentation-ready 12–15 minute demo sequence,
  covering manifest/provenance, Neo4j schema and multi-hop queries, derived facts,
  QA, explainable recommendation, RDF/OWL/SPARQL and measured evidence.
- Root `ChecklistCSDLNCv2.XLS`: grading rubric used to order the report chapters
  and review the final report, slides and oral defense.

## Working rules and precedence

For facts about what runs today: source code/tests/configuration, then root
`README.md`. For intended scope and academic deliverables: the DOCX brief, then
report/slide outlines. The lecture decks explain theory and
motivation; they do not override repository behavior.

Keep raw external data and secrets out of Git. Preserve immutable raw inputs,
checksums/manifests for processed outputs, demo independence from network APIs,
and the ability to reproduce tests and experiments from documented commands.
For draw.io work, use the repository-local skill at
`.agents/skills/drawio/SKILL.md`; `AGENTS.md` makes this discovery rule explicit.
