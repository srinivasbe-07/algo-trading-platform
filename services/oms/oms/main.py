"""FastAPI surface for the OMS.

GET  /health
POST /orders                 - submit an order (idempotent)      -> ManagedOrder
GET  /orders                 - list all orders
GET  /orders/{id}            - fetch one order
POST /orders/{id}/route      - mark live at broker (NEW -> PENDING)
POST /orders/{id}/fills      - record a (partial) fill
POST /orders/{id}/cancel     - cancel an open order
GET  /positions              - current positions + realised P&L
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from libs.common.models import CanonicalOrder
from pydantic import BaseModel

from .book import OrderBook, OrderError
from .order import ManagedOrder

app = FastAPI(title="oms", version="0.1.0")
_book = OrderBook()


class HealthResponse(BaseModel):
    status: str
    service: str


class SubmitRequest(BaseModel):
    order: CanonicalOrder
    idempotency_key: str | None = None


class FillRequest(BaseModel):
    quantity: int
    price: float


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="oms")


@app.post("/orders", response_model=ManagedOrder, tags=["orders"])
def submit(req: SubmitRequest) -> ManagedOrder:
    return _book.submit(req.order, req.idempotency_key)


@app.get("/orders", response_model=list[ManagedOrder], tags=["orders"])
def list_orders() -> list[ManagedOrder]:
    return _book.list_orders()


@app.get("/orders/{order_id}", response_model=ManagedOrder, tags=["orders"])
def get_order(order_id: str) -> ManagedOrder:
    try:
        return _book.get(order_id)
    except OrderError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/orders/{order_id}/route", response_model=ManagedOrder, tags=["orders"])
def route_order(order_id: str) -> ManagedOrder:
    return _guard(lambda: _book.mark_pending(order_id))


@app.post("/orders/{order_id}/fills", response_model=ManagedOrder, tags=["orders"])
def fill_order(order_id: str, req: FillRequest) -> ManagedOrder:
    return _guard(lambda: _book.record_fill(order_id, req.quantity, req.price))


@app.post("/orders/{order_id}/cancel", response_model=ManagedOrder, tags=["orders"])
def cancel_order(order_id: str) -> ManagedOrder:
    return _guard(lambda: _book.cancel(order_id))


@app.get("/positions", tags=["positions"])
def positions() -> dict[str, object]:
    return {
        "positions": {s: p.quantity for s, p in _book.positions().items()},
        "realized_pnl": _book.realized_pnl,
    }


def _guard(action: object) -> ManagedOrder:
    try:
        return action()  # type: ignore[operator, no-any-return]
    except OrderError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
