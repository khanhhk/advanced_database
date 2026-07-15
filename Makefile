SHELL := /bin/bash

PYTHON ?= python3
VENV ?= .venv
LLM_VENV ?= .venv-llm
BIN := $(VENV)/bin
PY := $(BIN)/python
PIP := $(BIN)/pip
UVICORN := $(BIN)/uvicorn
PYTEST := $(BIN)/pytest
INSTALL_STAMP := $(VENV)/.installed

DATA_COUNT ?= 2000
API_HOST ?= 127.0.0.1
API_PORT ?= 8000
BENCH_ITERATIONS ?= 100
BENCH_SCALES ?= 5,100,1000,5000
SYNTHETIC_BENCH_ITERATIONS ?= 10

.DEFAULT_GOAL := help
.PHONY: help setup llm-setup llm-run test imdb-data data neo4j-snapshot runtime-prepare run experiments semantic-reasoning sparql-check evidence-summary evaluation-corpora review-gate neo4j-benchmark relational-benchmark stop clean clean-imdb-raw _env _neo4j _neo4j-test _load

help: ## Hiển thị các workflow cần dùng
	@awk 'BEGIN {FS = ":.*## "; printf "Movie Knowledge Graph workflows:\n\n"} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

$(PY):
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

$(INSTALL_STAMP): pyproject.toml $(PY)
	$(PIP) install -e '.[dev]'
	@touch $(INSTALL_STAMP)

_env:
	@test -f .env || cp .env.example .env

setup: _env $(INSTALL_STAMP) ## Khởi tạo .env, Python environment và toàn bộ thư viện
	@$(PIP) check
	@echo "Setup complete. Set TMDB_API_KEY in .env before running 'make data'."

llm-setup: ## Tạo môi trường riêng và cài vLLM cho Qwen3-8B-AWQ
	python3 -m venv $(LLM_VENV)
	$(LLM_VENV)/bin/pip install --upgrade pip 'vllm==0.25.0'
	$(LLM_VENV)/bin/pip uninstall -y torchcodec

llm-run: ## Chạy Qwen3-8B-AWQ local tại cổng 8001 bằng GPU
	VLLM_USE_FLASHINFER_SAMPLER=0 $(LLM_VENV)/bin/vllm serve Qwen/Qwen3-8B-AWQ --host 127.0.0.1 --port 8001 --max-model-len 4096 --gpu-memory-utilization 0.85

_neo4j:
	docker compose up -d --wait neo4j

_neo4j-test:
	docker compose --profile test up -d --wait neo4j-test

test: setup _neo4j-test ## Chạy toàn bộ test, gồm integration trên Neo4j test riêng
	RUN_NEO4J_TESTS=1 ALLOW_NEO4J_TEST_RESET=1 NEO4J_URI=bolt://localhost:7688 NEO4J_PASSWORD=test-password $(PYTEST) -q
	$(PY) -m compileall -q src experiments tests
	sha256sum -c .agents/memory/SOURCES.sha256

imdb-data: setup ## Tải duy nhất IMDb ratings dạng nén, bỏ qua nếu đã hợp lệ
	$(PY) -m src.ingestion.download_imdb

data: setup imdb-data ## Thu thập TMDB, lọc IMDb ratings và chuẩn hóa dữ liệu
	$(PY) -m src.ingestion.collect_tmdb --count $(DATA_COUNT)
	$(PY) -m src.processing.pipeline --input data/raw/tmdb_movies.json --output data/processed --imdb-ratings data/raw/imdb/title.ratings.tsv.gz
	@echo "Dataset ready in data/processed (see manifest.json)."

neo4j-snapshot: setup _neo4j ## Xuất snapshot thí nghiệm từ graph hiện có, không gọi API
	$(PY) experiments/export_neo4j_snapshot.py
	$(PY) -m src.processing.pipeline --input data/interim/neo4j_snapshot.json --output data/processed

_load: setup _neo4j
	@test -f data/processed/manifest.json || { echo "No real dataset found. Run: make data"; exit 1; }
	$(PY) -m src.kg.load_neo4j --processed-dir data/processed --skip-transform --replace

runtime-prepare: setup _neo4j ## Chỉ import khi dataset hoặc graph thay đổi
	@test -f data/processed/manifest.json || { echo "No real dataset found. Run: make data"; exit 1; }
	$(PY) -m src.runtime.prepare

run: runtime-prepare ## Kiểm tra runtime rồi chạy ứng dụng, không cài/import lại vô ích
	$(UVICORN) src.api.main:app --reload --host $(API_HOST) --port $(API_PORT)

experiments: setup _neo4j ## Sinh QA evaluation, benchmark và RDF export
	@test -f data/raw/tmdb_movies.json || { echo "No real dataset found. Run: make data"; exit 1; }
	$(PY) experiments/evaluate.py
	$(PY) experiments/evaluate_qa_neo4j.py
	$(PY) experiments/benchmark_queries.py --iterations $(SYNTHETIC_BENCH_ITERATIONS) --scales $(BENCH_SCALES)
	$(PY) -m src.kg.export_rdf
	$(PY) -m src.kg.semantic_reasoning
	$(PY) experiments/evaluate_recommendation_neo4j.py

semantic-reasoning: setup ## Materialize RDFS/OWL entailment và kiểm tra semantic consistency
	@test -f data/processed/movies.ttl || { echo "No RDF export found. Run: make experiments"; exit 1; }
	$(PY) -m src.kg.semantic_reasoning

sparql-check: setup ## Parse và chạy đủ 10 SPARQL query trên RDF đã materialize
	@test -f data/processed/movies.inferred.ttl || { echo "No inferred RDF found. Run: make semantic-reasoning"; exit 1; }
	$(PY) -m src.kg.sparql_catalog

evidence-summary: setup ## Sinh bảng Markdown/CSV và biểu đồ SVG từ result artifacts
	$(PY) experiments/build_evidence_summary.py

evaluation-corpora: setup ## Sinh các corpus silver có evidence để review độc lập
	$(PY) experiments/build_review_corpora.py
	$(PY) experiments/evaluate_entity_resolution.py experiments/labels/entity_resolution.json > experiments/results/entity_resolution.json
	$(PY) experiments/evaluate_reasoning.py experiments/labels/reasoning.json > experiments/results/reasoning.json
	$(PY) experiments/evaluate_recommendation.py experiments/labels/recommendation.json --input data/raw/tmdb_movies.json > experiments/results/recommendation.json

review-gate: setup ## Chặn claim human-reviewed nếu metadata review chưa đầy đủ/độc lập
	$(PY) experiments/validate_human_review.py experiments/labels/entity_resolution.json experiments/labels/reasoning.json experiments/labels/recommendation.json

neo4j-benchmark: setup _neo4j ## Benchmark end-to-end trên Neo4j thật, 100 lần/query mặc định
	$(PY) experiments/benchmark_neo4j.py --iterations $(BENCH_ITERATIONS)

relational-benchmark: setup ## Baseline SQLite cùng processed snapshot cho query tương đương
	@test -f data/processed/manifest.json || { echo "No real dataset found. Run: make data"; exit 1; }
	$(PY) experiments/benchmark_relational.py --iterations $(BENCH_ITERATIONS)

stop: ## Dừng ứng dụng Docker/Neo4j nhưng giữ data volume
	docker compose down

clean-imdb-raw: ## Xóa IMDb raw; processed data vẫn được giữ
	rm -f data/raw/imdb/title.ratings.tsv.gz data/raw/imdb/title.ratings.tsv.gz.metadata.json

clean: ## Xóa cache/build artifacts, giữ toàn bộ raw và processed data
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov build dist *.egg-info
