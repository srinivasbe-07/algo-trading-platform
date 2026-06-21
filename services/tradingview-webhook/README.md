# tradingview-webhook

Receives TradingView alerts and routes them through the same risk + order pipeline
as native strategies (Phase 2).

Flow: **TradingView alert → this receiver → Risk Engine → OMS → paper broker.**

## Auth
TradingView can only send a URL + message body (no custom headers), so:
- a shared **passphrase** inside the JSON payload, and
- an **IP allowlist** of TradingView's published webhook IPs (enable in prod).

Set the passphrase via `TVHOOK_PASSPHRASE`; enable IP checks via `TVHOOK_IP_CHECK=true`.

## Alert payload (set this as the alert message in TradingView)
```json
{ "passphrase": "<secret>", "symbol": "NIFTY", "action": "BUY",
  "quantity": 50, "price": 20000, "order_type": "MARKET", "strategy": "orb" }
```

## Run
```bash
uvicorn tradingview_webhook.main:app --reload --app-dir services/tradingview-webhook
# POST http://localhost:8000/webhook/tradingview
```
