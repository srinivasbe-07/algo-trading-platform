"""The OMS core: an in-memory order book with a strict lifecycle state machine.

Responsibilities (per the architecture doc, section 4):
  - assign IDs and track every order through its lifecycle
  - idempotency: the same client key never creates two orders
  - position keeping: fills update broker-agnostic positions

State persists in memory for Phase 2 (lean). It moves to PostgreSQL — making the
order path recoverable after restart — when we wire persistence.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from libs.common.models import CanonicalOrder, OrderStatus, Position, Side

from .order import ManagedOrder


class OrderError(Exception):
    """Raised on an illegal state transition (e.g. filling a cancelled order)."""


class OrderBook:
    def __init__(self) -> None:
        self._orders: dict[str, ManagedOrder] = {}
        self._by_idempotency: dict[str, str] = {}
        self._positions: dict[str, Position] = {}
        self._realized_pnl: float = 0.0

    # ---- submission ---------------------------------------------------------
    def submit(self, order: CanonicalOrder, idempotency_key: str | None = None) -> ManagedOrder:
        """Accept a new order. A repeated idempotency key returns the same order."""
        if idempotency_key is not None and idempotency_key in self._by_idempotency:
            return self._orders[self._by_idempotency[idempotency_key]]

        managed = ManagedOrder(id=uuid.uuid4().hex, order=order, status=OrderStatus.NEW)
        self._orders[managed.id] = managed
        if idempotency_key is not None:
            self._by_idempotency[idempotency_key] = managed.id
        return managed

    def mark_pending(self, order_id: str) -> ManagedOrder:
        """Mark the order as live at the broker, awaiting fills."""
        managed = self._require(order_id)
        if managed.status is not OrderStatus.NEW:
            raise OrderError(f"cannot route order in state {managed.status}")
        return self._set_status(managed, OrderStatus.PENDING)

    # ---- fills --------------------------------------------------------------
    def record_fill(self, order_id: str, quantity: int, price: float) -> ManagedOrder:
        """Apply a (possibly partial) fill; update status and the position book."""
        managed = self._require(order_id)
        if managed.is_terminal:
            raise OrderError(f"cannot fill order in terminal state {managed.status}")
        if quantity <= 0 or quantity > managed.remaining_quantity:
            raise OrderError("invalid fill quantity")

        # Weighted-average fill price across partial fills.
        total = managed.filled_quantity + quantity
        managed.avg_fill_price = (
            managed.avg_fill_price * managed.filled_quantity + price * quantity
        ) / total
        managed.filled_quantity = total
        new_status = (
            OrderStatus.FILLED if managed.remaining_quantity == 0 else OrderStatus.PARTIALLY_FILLED
        )

        self._apply_to_position(managed.order, quantity, price)
        return self._set_status(managed, new_status)

    # ---- cancel / reject ----------------------------------------------------
    def cancel(self, order_id: str) -> ManagedOrder:
        managed = self._require(order_id)
        if managed.is_terminal:
            raise OrderError(f"cannot cancel order in terminal state {managed.status}")
        return self._set_status(managed, OrderStatus.CANCELLED)

    def reject(self, order_id: str, reason: str) -> ManagedOrder:
        managed = self._require(order_id)
        if managed.is_terminal:
            raise OrderError(f"cannot reject order in terminal state {managed.status}")
        managed.reject_reason = reason
        return self._set_status(managed, OrderStatus.REJECTED)

    # ---- queries ------------------------------------------------------------
    def get(self, order_id: str) -> ManagedOrder:
        return self._require(order_id)

    def list_orders(self) -> list[ManagedOrder]:
        return list(self._orders.values())

    def position(self, symbol: str) -> Position:
        return self._positions.setdefault(symbol, Position(symbol=symbol))

    def positions(self) -> dict[str, Position]:
        return self._positions

    @property
    def realized_pnl(self) -> float:
        return self._realized_pnl

    # ---- internals ----------------------------------------------------------
    def _require(self, order_id: str) -> ManagedOrder:
        if order_id not in self._orders:
            raise OrderError(f"unknown order id: {order_id}")
        return self._orders[order_id]

    def _set_status(self, managed: ManagedOrder, status: OrderStatus) -> ManagedOrder:
        managed.status = status
        managed.updated_at = datetime.now(timezone.utc)
        return managed

    def _apply_to_position(self, order: CanonicalOrder, quantity: int, price: float) -> None:
        side: Side = order.side
        position = self.position(order.symbol)
        self._realized_pnl += position.apply_fill(side, quantity, price)
