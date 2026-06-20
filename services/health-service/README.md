# health-service (template)

The reference microservice. Copy this folder to start a new service.

- `app/main.py` — FastAPI app with a `/health` probe
- `app/config.py` — env-based settings
- `tests/` — unit tests (also exercises shared `libs/common` models)
- `Dockerfile` — multi-stage, non-root runtime image

Run locally: `make run-health` then visit http://localhost:8000/health
