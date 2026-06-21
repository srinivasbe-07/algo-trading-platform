"""Tests for the alert handler routing through Risk + OMS + paper broker."""

from __future__ import annotations

from oms.book import OrderBook
from paper_trade.broker import PaperBroker
from risk_engine.config import RiskLimits
from risk_engine.engine import RiskEngine
from risk_engine.state import RiskState
from tradingview_webhook.handler import AlertHandler
from tradingview_webhook.models import AlertPayload


def _handler(**limits: object) -> AlertHandler:
    risk = RiskEngine(RiskLimits(**limits), RiskState(starting_equity=1_000_000.0))  # type: ignore[arg-type]
    return AlertHandler(risk, OrderBook(), PaperBroker())


def _alert(qty: int = 50) -> AlertPayload:
    return AlertPayload(passphrase="x", symbol="NIFTY", action="BUY", quantity=qty, price=20_000.0)


def test_valid_alert_is_filled() -> None:
    result = _handler().process(_alert())
    assert result["status"] == "filled"
    assert result["position"] == 50
    assert "order_id" in result


def test_alert_rejected_by_risk() -> None:
    result = _handler(max_order_quantity=10).process(_alert(qty=50))
    assert result["status"] == "rejected"
    assert any("quantity" in r for r in result["reasons"])  # type: ignore[union-attr]
