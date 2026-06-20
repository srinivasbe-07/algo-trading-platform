"""Tracks cash, position, realised P&L, and the equity curve over time."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Trade:
    timestamp: datetime
    side: str  # "BUY" or "SELL"
    quantity: int
    price: float  # fill price (after slippage)
    cost: float  # total charges on this trade
    realized_pnl: float  # realised P&L booked by this trade (0 for opening)


@dataclass
class Portfolio:
    cash: float
    position: int = 0
    avg_price: float = 0.0
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[tuple[datetime, float]] = field(default_factory=list)

    def apply_fill(
        self, timestamp: datetime, side: str, quantity: int, price: float, cost: float
    ) -> None:
        """Update cash/position from a fill and book realised P&L when reducing."""
        realized = 0.0
        signed = quantity if side == "BUY" else -quantity

        if self.position == 0 or (self.position > 0) == (signed > 0):
            # Opening or adding to a position: new weighted-average price.
            total_qty = self.position + signed
            if total_qty != 0:
                self.avg_price = (self.avg_price * self.position + price * signed) / total_qty
            self.position = total_qty
        else:
            # Reducing or flipping: realise P&L on the closed quantity.
            closing = min(abs(signed), abs(self.position))
            direction = 1 if self.position > 0 else -1
            realized = (price - self.avg_price) * closing * direction
            self.position += signed
            if self.position == 0:
                self.avg_price = 0.0
            elif (self.position > 0) != (direction > 0):
                # Flipped to the other side: remainder opens at fill price.
                self.avg_price = price

        self.cash += -price * signed - cost
        self.trades.append(Trade(timestamp, side, quantity, price, cost, realized))

    def equity(self, mark_price: float) -> float:
        """Total account value = cash + value of the open position."""
        return self.cash + self.position * mark_price

    def record_equity(self, timestamp: datetime, mark_price: float) -> None:
        self.equity_curve.append((timestamp, self.equity(mark_price)))
