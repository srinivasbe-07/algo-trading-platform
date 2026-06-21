"""Shared dry-run behaviour for all broker adapters.

Each concrete broker (Zerodha, Fyers, Dhan, Upstox, Delta Exchange) subclasses
this, sets its `name` and `required_credentials`, and inherits identical dry-run
order handling. The live path is guarded: it raises until credentials are present
and the broker's SDK is wired at go-live.
"""

from __future__ import annotations

import uuid

from libs.common.broker import BrokerError, BrokerOrderResult, Margins
from libs.common.models import CanonicalOrder, Position

from .config import BrokerConfig


class DryRunBrokerAdapter:
    name: str = "base"
    required_credentials: tuple[str, ...] = ()

    def __init__(
        self, config: BrokerConfig | None = None, credentials: dict[str, str] | None = None
    ) -> None:
        self._config = config or BrokerConfig()
        self._credentials = credentials or {}
        self._connected = False
        self._positions: dict[str, Position] = {}
        self._orders: dict[str, str] = {}

    @property
    def dry_run(self) -> bool:
        return self._config.dry_run

    def connect(self) -> None:
        if self._config.dry_run:
            self._connected = True
            return
        missing = [c for c in self.required_credentials if not self._credentials.get(c)]
        if missing:
            raise BrokerError(f"{self.name} live mode requires: {', '.join(missing)}")
        raise NotImplementedError(
            f"{self.name} live order placement is not enabled yet; wire the broker SDK at go-live."
        )

    def place_order(self, order: CanonicalOrder) -> BrokerOrderResult:
        if not self._connected:
            raise BrokerError("adapter not connected; call connect() first")
        if not self._config.dry_run:
            raise NotImplementedError(f"{self.name} live order placement not enabled")
        broker_order_id = uuid.uuid4().hex
        price = order.limit_price or 0.0
        position = self._positions.setdefault(order.symbol, Position(symbol=order.symbol))
        position.apply_fill(order.side, order.quantity, price)
        self._orders[broker_order_id] = "COMPLETE"
        return BrokerOrderResult(
            broker_order_id=broker_order_id,
            status="COMPLETE",
            filled_quantity=order.quantity,
            average_price=price,
        )

    def cancel_order(self, broker_order_id: str) -> None:
        if broker_order_id not in self._orders:
            raise BrokerError(f"unknown broker order id: {broker_order_id}")
        if self._orders[broker_order_id] == "COMPLETE":
            raise BrokerError("cannot cancel a completed order")
        self._orders[broker_order_id] = "CANCELLED"

    def get_positions(self) -> list[Position]:
        return list(self._positions.values())

    def get_margins(self) -> Margins:
        if not self._config.dry_run:
            raise NotImplementedError(f"{self.name} live margins not enabled")
        return Margins(available_cash=1_000_000.0)
