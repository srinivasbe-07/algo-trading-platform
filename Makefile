.PHONY: install hooks lint format type complexity security test cov check run-health up down build

install:        ## Install project + dev tooling
	pip install -e ".[dev]"

hooks:          ## Install pre-commit git hooks
	pre-commit install

lint:           ## Ruff lint
	ruff check .

format:         ## Ruff format check
	ruff format --check .

type:           ## mypy type check
	mypy services libs

complexity:     ## Cyclomatic complexity report (fails > C)
	radon cc -s -n C services libs

security:       ## Bandit SAST
	bandit -q -r services libs -c pyproject.toml

test:           ## Run tests
	pytest

cov:            ## Run tests with coverage gate
	pytest --cov --cov-report=term-missing --cov-report=xml

check: lint format type complexity security cov  ## Run the full local quality gate

run-health:     ## Run the template service locally
	uvicorn app.main:app --reload --app-dir services/health-service

up:             ## Start local stack
	docker compose up --build

down:
	docker compose down -v
