"""FastAPI surface for the Paper Trading Engine.

GET  /health
POST /paper/run  - run a paper session (MA-crossover on the replay feed) and
                   return the summary (orders, fills, rejections, equity, P&L).
"""

from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI
from oms.book import OrderBook
from pydantic import BaseModel
from risk_engine.config import RiskLimits
from risk_engine.engine import RiskEngine
from risk_engine.state import RiskState
from strategies.ma_crossover import MACrossover

from .broker import PaperBroker
from .engine import PaperTradingEngine
from .feed import replay_csv

app = FastAPI(title="paper-trade", version="0.1.0")


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="paper-trade")


@app.post("/paper/run", tags=["paper"])
def paper_run(fast: int = 10, slow: int = 20, quantity: int = 50) -> dict[str, object]:
    """Run a fresh paper session through the full Risk + OMS pipeline."""
    starting = 1_000_000.0
    risk = RiskEngine(RiskLimits(), RiskState(starting_equity=starting))
    engine = PaperTradingEngine(risk, OrderBook(), PaperBroker(), starting_equity=starting)
    result = engine.run(MACrossover(fast=fast, slow=slow, quantity=quantity), replay_csv())

    payload = asdict(result)
    payload["return_pct"] = result.return_pct
    # equity_curve tuples -> serialisable points
    payload["equity_curve"] = [
        {"time": ts.date().isoformat(), "value": v} for ts, v in result.equity_curve
    ]
    return payload
