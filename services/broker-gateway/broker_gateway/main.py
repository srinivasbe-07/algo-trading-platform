"""FastAPI surface for the Broker Gateway (dry-run by default).

GET  /health
GET  /broker/info        - which broker + dry-run status
POST /broker/orders      - place an order through the bound adapter
POST /broker/orders/{id}/cancel
GET  /broker/positions   - broker-reported positions
GET  /broker/margins     - available funds
POST /broker/reconcile   - compare supplied internal positions vs broker
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from libs.common.broker import BrokerError, BrokerOrderResult
from libs.common.models import CanonicalOrder
from pydantic import BaseModel

from .config import BrokerConfig
from .gateway import BrokerGateway
from .kite_adapter import ZerodhaKiteAdapter

app = FastAPI(title="broker-gateway", version="0.1.0")

_config = BrokerConfig()
_gateway = BrokerGateway(ZerodhaKiteAdapter(_config))


class HealthResponse(BaseModel):
    status: str
    service: str


class ReconcileRequest(BaseModel):
    internal_positions: dict[str, int]


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="broker-gateway")


@app.get("/broker/info", tags=["broker"])
def broker_info() -> dict[str, object]:
    return {"broker": _gateway.broker_name, "dry_run": _config.dry_run}


@app.post("/broker/orders", response_model=BrokerOrderResult, tags=["broker"])
def place_order(order: CanonicalOrder) -> BrokerOrderResult:
    try:
        return _gateway.place_order(order)
    except BrokerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/broker/orders/{broker_order_id}/cancel", tags=["broker"])
def cancel_order(broker_order_id: str) -> dict[str, str]:
    try:
        _gateway.cancel_order(broker_order_id)
    except BrokerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "cancelled", "broker_order_id": broker_order_id}


@app.get("/broker/positions", tags=["broker"])
def positions() -> dict[str, int]:
    return {p.symbol: p.quantity for p in _gateway.positions()}


@app.get("/broker/margins", tags=["broker"])
def margins() -> dict[str, float]:
    m = _gateway.margins()
    return {"available_cash": m.available_cash, "used_margin": m.used_margin, "total": m.total}


@app.post("/broker/reconcile", tags=["broker"])
def reconcile(req: ReconcileRequest) -> dict[str, object]:
    discrepancies = _gateway.reconcile(req.internal_positions)
    return {"in_sync": not discrepancies, "discrepancies": discrepancies}
