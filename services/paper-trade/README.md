# paper-trade (Paper Trading Engine)

The orchestrator that brings Phase 2 together (Phase 2).

Runs a strategy in real time over a replay feed, routing every order through the
real execution pipeline: **Strategy → OMS → Risk Engine → simulated broker**.
Same code path as live trading — only the broker is simulated, so no capital is
at risk. Orders decided at a bar's close fill at the next bar's open (no look-ahead).

- `feed.py` — replay the bundled sample CSV as a live Bar stream.
- `broker.py` — `PaperBroker`: simulated fills with slippage + costs.
- `engine.py` — `PaperTradingEngine`: the orchestration loop + result.
- `main.py` — FastAPI `/health`, `/paper/run`.

## Run

```bash
uvicorn paper_trade.main:app --reload --app-dir services/paper-trade
# POST http://localhost:8000/paper/run
```
