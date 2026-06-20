"""FastAPI surface for the backtest service.

Endpoints:
  GET /health           - liveness probe
  GET /backtest/sample  - run the example backtest, return metrics (JSON)
  GET /backtest/detail  - same run plus the data series the UI needs to chart
                          (price bars, equity curve, trade markers)
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from libs.common.market import Bar
from pydantic import BaseModel
from strategies.ma_crossover import MACrossover

from .analytics import analyze
from .data_feed import CSVDataFeed
from .engine import Backtester
from .portfolio import Portfolio

app = FastAPI(title="backtest-service", version="0.1.0")

# Allow the local Vite dev server (and configured origins) to call the API.
# Backtesting touches no money or secrets, so this is safe in development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SAMPLE_CSV = _REPO_ROOT / "data" / "sample_nifty.csv"


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="backtest-service")


def _run(fast: int, slow: int, quantity: int) -> tuple[list[Bar], Portfolio]:
    bars = list(CSVDataFeed(_SAMPLE_CSV))
    strategy = MACrossover(fast=fast, slow=slow, quantity=quantity)
    portfolio = Backtester().run(strategy, bars)
    return bars, portfolio


@app.get("/backtest/sample", tags=["backtest"])
def backtest_sample(fast: int = 10, slow: int = 20, quantity: int = 50) -> dict[str, object]:
    _, portfolio = _run(fast, slow, quantity)
    return asdict(analyze(portfolio))


@app.get("/backtest/detail", tags=["backtest"])
def backtest_detail(fast: int = 10, slow: int = 20, quantity: int = 50) -> dict[str, object]:
    """Metrics plus the chart series consumed by the frontend dashboard."""
    bars, portfolio = _run(fast, slow, quantity)
    return {
        "metrics": asdict(analyze(portfolio)),
        "bars": [
            {
                "time": b.timestamp.date().isoformat(),
                "open": b.open,
                "high": b.high,
                "low": b.low,
                "close": b.close,
            }
            for b in bars
        ],
        "equity": [
            {"time": ts.date().isoformat(), "value": value} for ts, value in portfolio.equity_curve
        ],
        "trades": [
            {"time": t.timestamp.date().isoformat(), "side": t.side, "price": t.price}
            for t in portfolio.trades
        ],
    }
