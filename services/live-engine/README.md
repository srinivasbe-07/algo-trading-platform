# live-engine

Wires the full execution path to a real broker adapter (Phase 3).

Runs a strategy through **Strategy → Risk → OMS → Broker Gateway**, then reconciles
the OMS position book against the broker's reported positions. Dry-run by default
(the Zerodha adapter records orders locally, sends nothing).

Going live is a config change only — real Kite credentials + `BROKER_DRY_RUN=false` —
the engine and pipeline are unchanged.

## Run (dry-run)
```bash
uvicorn live_engine.main:app --reload --app-dir services/live-engine
# POST /live/run  -> summary incl. "reconciled": true
```
