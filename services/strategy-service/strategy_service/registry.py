"""In-memory registry of strategy definitions (Postgres-backed later)."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class StrategySpec(BaseModel):
    name: str
    type: str = "ma_crossover"
    instrument: str = "NIFTY"
    fast: int = Field(default=10, gt=0)
    slow: int = Field(default=20, gt=1)
    quantity: int = Field(default=50, gt=0)
    max_position: int = Field(default=200, ge=0)
    daily_loss: float = Field(default=50_000.0, ge=0)


class Strategy(StrategySpec):
    id: str


class StrategyError(Exception):
    """Raised when a strategy id is not found."""


class StrategyRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Strategy] = {}

    def create(self, spec: StrategySpec) -> Strategy:
        strategy = Strategy(id=uuid.uuid4().hex, **spec.model_dump())
        self._items[strategy.id] = strategy
        return strategy

    def list(self) -> list[Strategy]:
        return list(self._items.values())

    def get(self, strategy_id: str) -> Strategy:
        if strategy_id not in self._items:
            raise StrategyError(f"unknown strategy id: {strategy_id}")
        return self._items[strategy_id]

    def delete(self, strategy_id: str) -> None:
        if strategy_id not in self._items:
            raise StrategyError(f"unknown strategy id: {strategy_id}")
        del self._items[strategy_id]
