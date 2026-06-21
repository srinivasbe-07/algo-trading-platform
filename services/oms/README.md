# oms (Order Management System)

The book of record for every order (Phase 2).

- `order.py` — `ManagedOrder`: an order plus its lifecycle state, fills, timestamps.
- `book.py` — `OrderBook`: submit (idempotent), route, fill (partial/full), cancel,
  reject, with a strict state machine; keeps broker-agnostic positions.
- `main.py` — FastAPI endpoints.

Lifecycle: NEW → PENDING → PARTIALLY_FILLED → FILLED (or REJECTED / CANCELLED).
State is in-memory for now; PostgreSQL persistence (recoverable order path) later.

## Run

```bash
uvicorn oms.main:app --reload --app-dir services/oms
```
