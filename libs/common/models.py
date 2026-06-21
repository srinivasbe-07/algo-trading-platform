"""Canonical domain models shared across services.

Broker-agnostic so one order/position model flows through strategy, risk, OMS,
and every broker adapter. Extended in Phase 2 with order lifecycle, positions,
and risk-decision types.
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


class OrderStatus(str, Enum):
    """Lifecycle states tracked by the OMS."""

    NEW = "NEW"
    PENDING = "PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class RiskDecisionType(str, Enum):
    APPROVED = "APPROVED"
    MODIFIED = "MODIFIED"
    REJECTED = "REJECTED"


class CanonicalOrder(BaseModel):
    """Broker-agnostic order intent. Adapters translate this to each broker's API."""

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


class Position(BaseModel):
    """A signed position in one instrument. Mutated as fills arrive."""

    symbol: str
    quantity: int = 0  # positive = long, negative = short
    avg_price: float = 0.0

    def notional(self, price: float) -> float:
        return abs(self.quantity) * price

    def apply_fill(self, side: Side, quantity: int, price: float) -> float:
        """Apply a fill; return realised P&L booked when reducing/closing."""
        signed = quantity if side is Side.BUY else -quantity
        realized = 0.0

        if self.quantity == 0 or (self.quantity > 0) == (signed > 0):
            total = self.quantity + signed
            if total != 0:
                self.avg_price = (self.avg_price * self.quantity + price * signed) / total
            self.quantity = total
        else:
            closing = min(abs(signed), abs(self.quantity))
            direction = 1 if self.quantity > 0 else -1
            realized = (price - self.avg_price) * closing * direction
            self.quantity += signed
            if self.quantity == 0:
                self.avg_price = 0.0
            elif (self.quantity > 0) != (direction > 0):
                self.avg_price = price
        return realized


class RiskDecision(BaseModel):
    """Result of a pre-trade risk check."""

    decision: RiskDecisionType
    order: CanonicalOrder
    reasons: list[str] = Field(default_factory=list)

    @property
    def approved(self) -> bool:
        return self.decision is not RiskDecisionType.REJECTED
