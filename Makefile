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

.DEFAULT_GOAL := help
.PHONY: help setup data demo run test stop llm-setup llm-run \
	_env _imdb-data _neo4j _neo4j-test _runtime-prepare

help: ## Liệt kê các lệnh phục vụ demo
	@printf '%s\n' \
		'Movie Knowledge Graph — demo commands' \
		'' \
		'  make setup      Tạo môi trường Python và file .env' \
		'  make data       Thu thập, enrich và chuẩn hóa dữ liệu' \
		'  make demo       Dựng Neo4j, import khi cần và chạy API/UI' \
		'  make test       Chạy unit/API và integration test riêng' \
		'  make stop       Dừng các service Docker, giữ dữ liệu' \
		'' \
		'Optional local LLM planner:' \
		'  make llm-setup  Cài Qwen/vLLM vào .venv-llm' \
		'  make llm-run    Chạy planner tại 127.0.0.1:8001'

$(PY):
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

$(INSTALL_STAMP): pyproject.toml $(PY)
	$(PIP) install -e '.[dev]'
	@touch $(INSTALL_STAMP)

_env:
	@test -f .env || cp .env.example .env

setup: _env $(INSTALL_STAMP) ## Chuẩn bị môi trường chạy demo
	@$(PIP) check
	@echo "Setup complete. Configure TMDB_API_KEY only when collecting new data."

_imdb-data: setup
	$(PY) -m src.ingestion.download_imdb

data: setup _imdb-data ## Chuẩn bị snapshot dữ liệu thật
	$(PY) -m src.ingestion.collect_tmdb --count $(DATA_COUNT)
	$(PY) -m src.processing.pipeline \
		--input data/raw/tmdb_movies.json \
		--output data/processed \
		--imdb-ratings data/raw/imdb/title.ratings.tsv.gz
	@echo "Dataset ready: data/processed/manifest.json"

_neo4j:
	docker compose up -d --wait neo4j

_neo4j-test:
	docker compose --profile test up -d --wait neo4j-test

_runtime-prepare: setup _neo4j
	@test -f data/processed/manifest.json || { \
		echo "Missing processed data. Run: make data"; \
		exit 1; \
	}
	$(PY) -m src.runtime.prepare

demo: _runtime-prepare ## Chạy API và giao diện demo
	@echo "Demo UI: http://$(API_HOST):$(API_PORT)/"
	@echo "Swagger: http://$(API_HOST):$(API_PORT)/docs"
	$(UVICORN) src.api.main:app --host $(API_HOST) --port $(API_PORT)

# Backward-compatible alias; keep the public demo workflow centered on `make demo`.
run: demo

test: setup _neo4j-test ## Chạy toàn bộ kiểm thử trên Neo4j test riêng
	RUN_NEO4J_TESTS=1 ALLOW_NEO4J_TEST_RESET=1 \
		NEO4J_URI=bolt://localhost:7688 NEO4J_PASSWORD=test-password \
		$(PYTEST) -q
	$(PY) -m compileall -q src experiments tests
	sha256sum -c .agents/memory/SOURCES.sha256

llm-setup: ## Cài optional local Qwen planner
	$(PYTHON) -m venv $(LLM_VENV)
	$(LLM_VENV)/bin/pip install --upgrade pip 'vllm==0.25.0'
	$(LLM_VENV)/bin/pip uninstall -y torchcodec

llm-run: ## Chạy optional local Qwen planner
	VLLM_USE_FLASHINFER_SAMPLER=0 $(LLM_VENV)/bin/vllm serve \
		Qwen/Qwen3-8B-AWQ \
		--host 127.0.0.1 \
		--port 8001 \
		--max-model-len 4096 \
		--gpu-memory-utilization 0.85

stop: ## Dừng service demo và giữ data volume
	docker compose down
