"""FastAPI surface for the Live Trading Engine.

  GET  /health
  POST /live/run  - run a strategy through Risk → OMS → Broker Gateway (dry-run)
                    and return the summary + reconciliation status.

Dry-run by default (no real orders). Going live = real broker credentials +
BROKER_DRY_RUN=false; this endpoint and the engine are unchanged.
"""

from __future__ import annotations

from dataclasses import asdict

from broker_gateway.adapters import build_adapter
from broker_gateway.config import BrokerConfig
from broker_gateway.gateway import BrokerGateway
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from libs.common.feed import load_bars
from oms.book import OrderBook
from pydantic import BaseModel
from risk_engine.config import RiskLimits
from risk_engine.engine import RiskEngine
from risk_engine.state import RiskState
from strategies.ma_crossover import MACrossover

from .engine import LiveTradingEngine

app = FastAPI(title="live-engine", version="0.1.0")

# Allow the local Vite dev server to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="live-engine")


@app.post("/live/run", tags=["live"])
def live_run(fast: int = 10, slow: int = 20, quantity: int = 50) -> dict[str, object]:
    starting = 1_000_000.0
    risk = RiskEngine(RiskLimits(), RiskState(starting_equity=starting))
    config = BrokerConfig()
    gateway = BrokerGateway(build_adapter(config.broker, config))
    engine = LiveTradingEngine(risk, OrderBook(), gateway, starting_equity=starting)
    result = engine.run(MACrossover(fast=fast, slow=slow, quantity=quantity), load_bars())

    payload = asdict(result)
    payload["return_pct"] = result.return_pct
    payload["equity_curve"] = [
        {"time": ts.date().isoformat(), "value": v} for ts, v in result.equity_curve
    ]
    return payload
