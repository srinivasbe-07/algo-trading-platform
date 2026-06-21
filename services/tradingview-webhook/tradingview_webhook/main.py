"""FastAPI surface for the TradingView webhook receiver.

  GET  /health
  POST /webhook/tradingview  - authenticate (IP + passphrase), validate, route.

A single in-process Risk + OMS + paper broker acts as the paper account for the
demo. The endpoint returns whether the alert was filled or rejected (with reasons).
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from oms.book import OrderBook
from paper_trade.broker import PaperBroker
from pydantic import BaseModel
from risk_engine.config import RiskLimits
from risk_engine.engine import RiskEngine
from risk_engine.state import RiskState

from .config import WebhookConfig
from .handler import AlertHandler
from .models import AlertPayload
from .security import ip_allowed, passphrase_ok

app = FastAPI(title="tradingview-webhook", version="0.1.0")

_config = WebhookConfig()
_handler = AlertHandler(
    RiskEngine(RiskLimits(), RiskState(starting_equity=1_000_000.0)),
    OrderBook(),
    PaperBroker(),
)


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="tradingview-webhook")


@app.post("/webhook/tradingview", tags=["webhook"])
def tradingview_webhook(payload: AlertPayload, request: Request) -> dict[str, object]:
    client_ip = request.client.host if request.client else ""
    if not ip_allowed(client_ip, _config.allowed_ips, _config.ip_check_enabled):
        raise HTTPException(status_code=403, detail="source IP not allowed")
    if not passphrase_ok(payload.passphrase, _config.passphrase):
        raise HTTPException(status_code=403, detail="invalid passphrase")
    return _handler.process(payload)
