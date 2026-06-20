# Algo Trading Platform

End-to-end algorithmic trading platform — strategy authoring, backtesting, paper
trading, risk management, and multi-broker execution (Indian + global) built as
Python microservices on managed cloud infrastructure.

See `docs/Algo_Trading_Platform_Architecture.docx` for the full design.

## Status — Phase 0: Foundation

The repository skeleton, code-quality tooling, a service template, and the CI/CD
pipeline. Every push to GitHub runs: compile → lint → format check → type check →
complexity → security (SAST) → tests + coverage gate → dependency & image scan.

## Layout

```
algo-trading-platform/
├─ services/            # one folder per microservice (health-service = template)
├─ libs/                # shared code: canonical models, broker contracts, utils
├─ strategies/          # versioned user strategies
├─ infra/terraform/     # infrastructure as code (AWS)
├─ tests/               # cross-service end-to-end tests
├─ .github/workflows/   # CI/CD pipeline
├─ pyproject.toml       # tooling config (ruff, mypy, pytest, coverage, bandit)
└─ docker-compose.yml   # local dev stack
```

## Quick start

```bash
# 1. Create and activate a virtual environment
python3.12 -m venv .venv && source .venv/bin/activate

# 2. Install the project with dev tooling
pip install -e ".[dev]"

# 3. Install git hooks
pre-commit install

# 4. Run the quality gate locally (same checks as CI)
make check

# 5. Run the template service
make run-health     # then open http://localhost:8000/health
```

## Roadmap

| Phase | Focus |
|-------|-------|
| 0 | Foundation: repo, CI/CD, tooling, service template (this) |
| 1 | Backtesting engine + strategy interface |
| 2 | Market data, OMS, Risk Engine, paper trading |
| 3 | Live trading — Zerodha Kite |
| 4 | Multi-broker (Angel One, Upstox/Dhan/Fyers, IBKR/Alpaca) + scale |
| 5 | Hardening, dashboards, compliance reporting |
