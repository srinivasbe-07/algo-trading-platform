"""The Broker Gateway: a thin uniform facade over whichever broker adapter is
bound, plus position reconciliation (our records vs the broker's).
"""

from __future__ import annotations

from libs.common.broker import BrokerAdapter, BrokerOrderResult, Margins
from libs.common.models import CanonicalOrder, Position


class BrokerGateway:
    def __init__(self, adapter: BrokerAdapter) -> None:
        self._adapter = adapter
        self._adapter.connect()

    @property
    def broker_name(self) -> str:
        return self._adapter.name

    def place_order(self, order: CanonicalOrder) -> BrokerOrderResult:
        return self._adapter.place_order(order)

    def cancel_order(self, broker_order_id: str) -> None:
        self._adapter.cancel_order(broker_order_id)

    def positions(self) -> list[Position]:
        return self._adapter.get_positions()

    def margins(self) -> Margins:
        return self._adapter.get_margins()

    def reconcile(self, internal_positions: dict[str, int]) -> list[dict[str, object]]:
        """Compare our positions against the broker's; return any mismatches."""
        broker = {p.symbol: p.quantity for p in self._adapter.get_positions()}
        out: list[dict[str, object]] = []
        for symbol in set(internal_positions) | set(broker):
            ours = internal_positions.get(symbol, 0)
            theirs = broker.get(symbol, 0)
            if ours != theirs:
                out.append({"symbol": symbol, "internal": ours, "broker": theirs})
        return out
