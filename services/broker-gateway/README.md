# broker-gateway

The uniform door to every broker (Phase 3).

Exposes the canonical `BrokerAdapter` interface (`libs/common/broker.py`) and binds
one adapter. A new broker = a new adapter, with no change to risk/OMS/strategy code.

- `kite_adapter.py` — Zerodha Kite adapter. **Dry-run by default** (validates +
  records orders locally, sends nothing). Live wiring is guarded until go-live.
- `gateway.py` — `BrokerGateway` facade + position reconciliation.
- `main.py` — FastAPI endpoints.

## Go live (later)
Set credentials and disable dry-run:
```bash
export KITE_API_KEY=... KITE_API_SECRET=... KITE_ACCESS_TOKEN=...
export BROKER_DRY_RUN=false
```
Order traffic must egress from a SEBI-registered static IP.

## Run (dry-run)
```bash
uvicorn broker_gateway.main:app --reload --app-dir services/broker-gateway
# GET /broker/info  -> {"broker":"zerodha-kite","dry_run":true}
```
