"""Turns a validated alert into an order and routes it through the SAME pipeline
as native strategies: Risk → OMS → paper broker. The receiver never bypasses
risk controls — it only translates and authenticates.
"""

from __future__ import annotations

from libs.common.models import CanonicalOrder, OrderType
from oms.book import OrderBook
from paper_trade.broker import PaperBroker
from risk_engine.engine import RiskEngine

from .models import AlertPayload


class AlertHandler:
    def __init__(self, risk: RiskEngine, oms: OrderBook, broker: PaperBroker) -> None:
        self._risk = risk
        self._oms = oms
        self._broker = broker

    def process(self, alert: AlertPayload) -> dict[str, object]:
        order = CanonicalOrder(
            symbol=alert.symbol,
            side=alert.action,
            quantity=alert.quantity,
            order_type=alert.order_type,
            limit_price=alert.price if alert.order_type is OrderType.LIMIT else None,
        )

        decision = self._risk.check(order, alert.price, strategy=alert.strategy)
        if not decision.approved:
            return {"status": "rejected", "reasons": decision.reasons}

        managed = self._oms.submit(order, idempotency_key=alert.alert_id)
        self._oms.mark_pending(managed.id)
        fill_price, _cost = self._broker.simulate_fill(alert.action, alert.quantity, alert.price)
        self._oms.record_fill(managed.id, alert.quantity, fill_price)
        self._risk.record_fill(order, fill_price, alert.quantity)

        return {
            "status": "filled",
            "order_id": managed.id,
            "fill_price": fill_price,
            "position": self._oms.position(alert.symbol).quantity,
        }
