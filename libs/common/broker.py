"""The canonical broker interface — the contract every broker adapter implements.

Shared (libs/common) so the OMS / live engine talks to ONE interface and a new
broker is added by writing an adapter — no change to strategy, risk, or OMS code.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from libs.common.models import CanonicalOrder, Position


class Margins(BaseModel):
    """Funds available to trade, as reported by the broker."""

    available_cash: float
    used_margin: float = 0.0

    @property
    def total(self) -> float:
        return self.available_cash + self.used_margin


class BrokerOrderResult(BaseModel):
    """What a broker returns after accepting an order."""

    broker_order_id: str
    status: str  # COMPLETE / OPEN / REJECTED / CANCELLED
    filled_quantity: int = 0
    average_price: float = 0.0


class BrokerError(Exception):
    """Raised on broker connection or order errors."""


@runtime_checkable
class BrokerAdapter(Protocol):
    """One uniform interface; each broker (Zerodha, Angel One, IBKR…) implements it."""

    name: str

    def connect(self) -> None: ...

    def place_order(self, order: CanonicalOrder) -> BrokerOrderResult: ...

    def cancel_order(self, broker_order_id: str) -> None: ...

    def get_positions(self) -> list[Position]: ...

    def get_margins(self) -> Margins: ...
