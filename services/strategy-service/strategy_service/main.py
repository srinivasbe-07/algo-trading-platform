"""FastAPI surface for the strategy registry.

GET    /health
POST   /strategies        - create a strategy           -> Strategy
GET    /strategies        - list all strategies
GET    /strategies/{id}   - fetch one
DELETE /strategies/{id}   - remove one
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .registry import Strategy, StrategyError, StrategyRegistry, StrategySpec

app = FastAPI(title="strategy-service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_registry = StrategyRegistry()


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="strategy-service")


@app.post("/strategies", response_model=Strategy, tags=["strategies"])
def create_strategy(spec: StrategySpec) -> Strategy:
    return _registry.create(spec)


@app.get("/strategies", response_model=list[Strategy], tags=["strategies"])
def list_strategies() -> list[Strategy]:
    return _registry.list()


@app.get("/strategies/{strategy_id}", response_model=Strategy, tags=["strategies"])
def get_strategy(strategy_id: str) -> Strategy:
    try:
        return _registry.get(strategy_id)
    except StrategyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/strategies/{strategy_id}", tags=["strategies"])
def delete_strategy(strategy_id: str) -> dict[str, str]:
    try:
        _registry.delete(strategy_id)
    except StrategyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "deleted", "id": strategy_id}
