# strategy-service

Registry of saved strategy definitions (Phase 2/UI). In-memory for now;
PostgreSQL-backed later.

- `registry.py` — `StrategySpec`/`Strategy` models + `StrategyRegistry` (create/list/get/delete).
- `main.py` — FastAPI CRUD endpoints with CORS for the dashboard.

## Run
```bash
python run.py strategy   # -> http://localhost:8006
```
