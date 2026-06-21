"""The managed order record tracked through its lifecycle by the OMS."""

from __future__ import annotations

from datetime import datetime, timezone

from libs.common.models import CanonicalOrder, OrderStatus
from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ManagedOrder(BaseModel):
    """An order plus everything the OMS tracks about its progress."""

    id: str
    order: CanonicalOrder
    status: OrderStatus = OrderStatus.NEW
    filled_quantity: int = 0
    avg_fill_price: float = 0.0
    reject_reason: str | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    @property
    def remaining_quantity(self) -> int:
        return self.order.quantity - self.filled_quantity

    @property
    def is_terminal(self) -> bool:
        """True once the order can no longer change (done, rejected, cancelled)."""
        return self.status in (
            OrderStatus.FILLED,
            OrderStatus.REJECTED,
            OrderStatus.CANCELLED,
        )
