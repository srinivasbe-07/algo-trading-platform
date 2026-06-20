"""Canonical domain models shared across services.

These are deliberately minimal in Phase 0; they grow as the execution plane is
built out in later phases. Keeping them broker-agnostic is what lets a single
order/position model flow through strategy, risk, OMS, and every broker adapter.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class TradingMode(str, Enum):
    """Same strategy code runs in each mode; only the broker adapter changes."""

    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    LIVE = "LIVE"


class CanonicalOrder(BaseModel):
    """Broker-agnostic order. Adapters translate this to each broker's API."""

    symbol: str
    side: Side
    quantity: int = Field(gt=0)
    order_type: OrderType = OrderType.MARKET
    limit_price: float | None = Field(default=None, gt=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def notional(self, reference_price: float) -> float:
        """Approximate cash value of the order at a reference price."""
        price = self.limit_price if self.limit_price is not None else reference_price
        return price * self.quantity
