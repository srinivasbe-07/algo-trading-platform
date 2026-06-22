"""FastAPI surface for the Risk Engine.

  GET  /health
  POST /risk/check   - pre-trade check for an order  -> RiskDecision
  POST /risk/fill    - record a fill (updates positions, P&L, real-time controls)
  POST /risk/kill    - trip the global kill-switch
  POST /risk/reset   - clear the kill-switch
  GET  /risk/state   - current risk state snapshot

State is in-memory for Phase 2 (single instance). Redis-backed state and
multi-instance support come when we scale.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from libs.common.models import CanonicalOrder, RiskDecision, Side
from pydantic import BaseModel

from .config import RiskLimits
from .engine import RiskEngine
from .state import RiskState

app = FastAPI(title="risk-engine", version="0.1.0")

# Allow the local Vite dev server (and configured origins) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# A single in-process engine for the demo. Wired to config/persistence later.
_engine = RiskEngine(RiskLimits(), RiskState(starting_equity=1_000_000.0))


class HealthResponse(BaseModel):
    status: str
    service: str


class CheckRequest(BaseModel):
    order: CanonicalOrder
    reference_price: float
    strategy: str | None = None


class FillRequest(BaseModel):
    symbol: str
    side: Side
    quantity: int
    fill_price: float


class KillRequest(BaseModel):
    reason: str = "manual"


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="risk-engine")


@app.post("/risk/check", response_model=RiskDecision, tags=["risk"])
def risk_check(req: CheckRequest) -> RiskDecision:
    return _engine.check(req.order, req.reference_price, req.strategy)


@app.post("/risk/fill", tags=["risk"])
def risk_fill(req: FillRequest) -> dict[str, str]:
    order = CanonicalOrder(symbol=req.symbol, side=req.side, quantity=req.quantity)
    _engine.record_fill(order, req.fill_price, req.quantity)
    return {"status": "recorded"}


@app.post("/risk/kill", tags=["risk"])
def risk_kill(req: KillRequest) -> dict[str, str]:
    _engine.trip_kill_switch(req.reason)
    return {"status": "kill-switch tripped", "reason": req.reason}


@app.post("/risk/reset", tags=["risk"])
def risk_reset() -> dict[str, str]:
    _engine.reset_kill_switch()
    return {"status": "kill-switch reset"}


@app.get("/risk/state", tags=["risk"])
def risk_state() -> dict[str, object]:
    s = _engine._state
    return {
        "equity": s.equity,
        "realized_pnl": s.realized_pnl,
        "kill_switch": s.kill_switch,
        "kill_reason": s.kill_reason,
        "positions": {k: v.quantity for k, v in s.positions.items()},
        "paused_strategies": sorted(s.paused_strategies),
    }
