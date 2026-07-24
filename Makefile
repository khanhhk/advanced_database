SHELL := /bin/bash

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
PY := $(BIN)/python
PIP := $(BIN)/pip
UVICORN := $(BIN)/uvicorn
PYTEST := $(BIN)/pytest
INSTALL_STAMP := $(VENV)/.installed

DATA_COUNT ?= 5000
API_HOST ?= 127.0.0.1
API_PORT ?= 8000

.DEFAULT_GOAL := help
.PHONY: help setup data demo test stop \
	_env _imdb-data _neo4j _neo4j-test _runtime-prepare

help: ## Liệt kê các lệnh phục vụ demo
	@printf '%s\n' \
		'Movie Knowledge Graph — demo commands' \
		'' \
		'  make setup      Tạo môi trường Python và file .env' \
		'  make data       Thu thập, enrich và chuẩn hóa dữ liệu' \
		'  make demo       Dựng Neo4j, import khi cần và chạy API/UI' \
		'  make test       Chạy unit/API và integration test riêng' \
		'  make stop       Dừng các service Docker, giữ dữ liệu'

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


test: setup _neo4j-test ## Chạy toàn bộ kiểm thử trên Neo4j test riêng
	RUN_NEO4J_TESTS=1 ALLOW_NEO4J_TEST_RESET=1 \
		NEO4J_URI=bolt://localhost:7688 NEO4J_PASSWORD=test-password \
		$(PYTEST) -q
	$(PY) -m compileall -q src experiments tests
	sha256sum -c .agents/memory/SOURCES.sha256

stop: ## Dừng service demo và giữ data volume
	docker compose down
