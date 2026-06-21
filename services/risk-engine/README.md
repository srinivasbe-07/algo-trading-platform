# risk-engine

The mandatory pre-trade and real-time risk checkpoint (Phase 2).

- `config.py` — configurable `RiskLimits` (order size, position caps, daily-loss,
  drawdown, order-rate, instrument whitelist/blacklist).
- `state.py` — live in-memory state (positions, realised P&L, kill-switch).
- `engine.py` — `check()` (pre-trade) and `record_fill()` (real-time controls).
- `main.py` — FastAPI endpoints.

Every order must pass `check()` before reaching a broker. `record_fill()` updates
positions/P&L and can auto-trip the kill-switch on a daily-loss or drawdown breach.

## Run

```bash
uvicorn risk_engine.main:app --reload --app-dir services/risk-engine
# POST http://localhost:8000/risk/check
```
