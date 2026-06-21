"""Zerodha Kite adapter.

In DRY-RUN mode it validates and records orders locally (no network, no money) so
the whole live path can be built and tested safely. The real wiring to the
`kiteconnect` SDK lives behind the `dry_run=False` branch and is intentionally
guarded until credentials and a static IP are in place (Phase 3 go-live).
"""

from __future__ import annotations

import uuid

from libs.common.broker import BrokerError, BrokerOrderResult, Margins
from libs.common.models import CanonicalOrder, Position

from .config import BrokerConfig


class ZerodhaKiteAdapter:
    name = "zerodha-kite"

    def __init__(self, config: BrokerConfig) -> None:
        self._config = config
        self._connected = False
        self._positions: dict[str, Position] = {}
        self._orders: dict[str, str] = {}  # broker_order_id -> status

    def connect(self) -> None:
        if self._config.dry_run:
            self._connected = True
            return
        # --- live path (guarded until go-live) ---
        if not (self._config.api_key and self._config.access_token):
            raise BrokerError("live mode requires KITE_API_KEY and KITE_ACCESS_TOKEN")
        raise NotImplementedError(
            "live Kite order placement is not enabled yet; provide credentials and "
            "wire kiteconnect at go-live (Phase 3)."
        )

    def place_order(self, order: CanonicalOrder) -> BrokerOrderResult:
        if not self._connected:
            raise BrokerError("adapter not connected; call connect() first")
        if self._config.dry_run:
            return self._dry_run_place(order)
        raise NotImplementedError("live order placement not enabled")

    def _dry_run_place(self, order: CanonicalOrder) -> BrokerOrderResult:
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
        if self._config.dry_run:
            return Margins(available_cash=1_000_000.0)
        raise NotImplementedError("live margins not enabled")
