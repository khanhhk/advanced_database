# Movie Knowledge Graph — project memory

Last reviewed: 2026-07-20. This briefing summarizes the original Office sources,
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
- RDF/RDFS/OWL, RDFLib and Protégé/Jena illustrate standards, semantic
  constraints, SPARQL and reasoner capabilities.
- The standards path is executable: RDFLib materializes the declared RDFS/OWL-RL
  subset (domain/range, inverse and symmetric properties) and validates functional
  properties, disjoint classes and required Movie titles. It reports before/after
  triple counts and violations; it is not presented as a full OWL 2 DL reasoner.
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
The evaluation workflow also provides a same-snapshot SQLite baseline for four
representative relational queries and generates CSV/Markdown/SVG evidence summaries.
Neo4j/SQLite comparisons are valid only when run on the same machine, dataset,
warm-up policy and iteration count.
The RDF workflow parses and executes all ten numbered SPARQL queries after
materialization. Administrative Movie CRUD is parameterized and tested but is
not exposed through the public API. Integration tests use a dedicated temporary
Neo4j service on Bolt 7688, so they can verify reset/import/idempotency, QA,
recommendation and CRUD without touching the demo graph.

Current reproducible evidence (data snapshot 2026-07-15; QA rerun 2026-07-20):
the pipeline receives 2,001 records,
explicitly rejects one relationship-free Movie, and retains 2,000 valid movies.
The loaded graph validates at 37,349 nodes/353,915 relationships with zero structural
violations. Exact IMDb ratings match 1,783 of 1,855 movies carrying an IMDb ID.
Silver entity-resolution P/R/F1 is 1.00; silver co-star precision is 1.00;
the strengthened 20-question Neo4j QA smoke corpus passes 20/20 with evidence,
including a negative assertion that `The Dark Knight` cast lookup excludes actors
linked only to `The Dark Knight Rises`; semantic
materialization adds 35,419 triples (154,970 to 190,389) with zero violations;
all ten SPARQL queries execute successfully.
The real Neo4j benchmark uses Neo4j 5.26.28, one warm-up and 100 iterations per
question at 2,000 movies; intent medians range 2.67–188.74 ms and p95 ranges
5.08–211.24 ms. This single-scale result is not a scalability claim. A controlled
same-snapshot SQLite baseline covers four equivalent queries and is faster on all
four; this supports a trade-off discussion, not a universal engine ranking.
On 20 silver cases against real Neo4j, the
IDF-weighted production ranker reaches P@10 0.715 and NDCG@10 0.754. Historical
results were overlap 0.67/0.723, weighted Jaccard 0.64/0.699, and hybrid
0.59/0.657; these remain design history rather than end-user alternatives.
Runtime preparation is idempotent: dependency stamps follow `pyproject.toml`,
while `runtime_manifest.json` plus the live Movie count decide whether import is
required. Normal `make run` reuses the graph.

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
- `docs/CODE_PLAN.md`: repository layout, implementation order, API/query/test
  requirements and engineering quality rules.
- `docs/REPORT_OUTLINE.md` and `docs/SLIDE_OUTLINE.md`: expected report and
  presentation story; keep final artifacts aligned with measured evidence.
- `docs/REPORT_DRAFT.md`: current ten-chapter Vietnamese report manuscript,
  including theory, related work, implementation, measured evidence, validity
  limits, preliminary IEEE-style references and reproducibility appendices. Its
  front matter and evaluation prose were streamlined on 2026-07-19 for the course
  submission; detailed defense notes now live in `docs/internal/REPORT_SUPPORT.md`.
- `report_latex/`: submission-oriented LaTeX report generated from the manuscript.
  `main.tex` assembles all ten chapters and appendices, `ref.bib` is the normalized
  bibliography, and all 14 image calls now resolve to vector PDF figures under
  `report_latex/images/`. Eleven editable diagram sources live in
  `report_latex/images/sources/*.drawio`; three measured charts are generated from
  experiment CSV/JSON. Regenerate them with
  `python3 scripts/generate_report_figures.py`. `web_ui.pdf` is explicitly a
  source-aligned wireframe and may later be replaced by a real screenshot with
  the same filename. Regenerate chapter files with
  `python3 scripts/report_markdown_to_latex.py` after manuscript edits.
- Root `README.md`: current runnable interface and commands; prefer it over old
  planning prose when describing implemented behavior.
- `docs/README.md`: index and precedence guidance for the planning documents.
- `docs/movie_knowledge_graph_flow.drawio`: editable current-architecture flow.
- `docs/ARCHITECTURE_EXPLAINED.md`: block-by-block and request-path explanation
  of the draw.io architecture.
- `docs/QWEN_VLLM_DEPLOYMENT.md`: reproducible GPU/vLLM/Qwen setup and
  troubleshooting runbook.
- `docs/DBEAVER_NEO4J_DEMO.md`: reproducible DBeaver Community demo runbook. It
  configures the official Neo4j JDBC full bundle as a custom Generic driver,
  documents SQL-to-Cypher versus native Cypher use, and covers connection and
  authentication troubleshooting for the local Compose graph.
- `docs/CHECKLIST_TRACEABILITY.md`: A-level release gate mapping each grading
  criterion to code/evidence and the future report/slide; source Office files are
  references, not submission deliverables.

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
