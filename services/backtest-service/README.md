# backtest-service

Event-driven backtesting engine (Phase 1).

- `backtest_engine/` — data feed, simulated broker + India cost model, portfolio,
  the event loop (`engine.py`), and performance analytics.
- `run_backtest.py` — CLI that backtests the example strategy on bundled data.
- `main.py` — FastAPI `/health` and `/backtest/sample` endpoints.

The strategy interface lives in `libs/common/strategy.py` (shared) so the same
strategy code will run in paper and live trading later.

## Run the example

```bash
python services/backtest-service/run_backtest.py
# or the API:
uvicorn backtest_engine.main:app --reload --app-dir services/backtest-service
# then GET http://localhost:8000/backtest/sample
```
