"""Live risk state. In-memory for Phase 2 (lean); Redis-backed when we scale."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from libs.common.models import Position


@dataclass
class RiskState:
    starting_equity: float
    realized_pnl: float = 0.0
    equity_high_water: float = 0.0
    positions: dict[str, Position] = field(default_factory=dict)
    order_times: deque[float] = field(default_factory=deque)  # epoch seconds
    kill_switch: bool = False
    kill_reason: str | None = None
    paused_strategies: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.equity_high_water = self.starting_equity

    @property
    def equity(self) -> float:
        return self.starting_equity + self.realized_pnl

    def position(self, symbol: str) -> Position:
        return self.positions.setdefault(symbol, Position(symbol=symbol))
