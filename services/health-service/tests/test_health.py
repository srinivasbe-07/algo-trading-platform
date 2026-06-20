"""Unit tests for the template service and shared models."""

from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient
from libs.common.models import CanonicalOrder, OrderType, Side

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "health-service"


def test_canonical_order_market_notional() -> None:
    order = CanonicalOrder(symbol="INFY", side=Side.BUY, quantity=10)
    assert order.order_type is OrderType.MARKET
    assert order.notional(reference_price=1500.0) == 15000.0


def test_canonical_order_limit_uses_limit_price() -> None:
    order = CanonicalOrder(
        symbol="TCS",
        side=Side.SELL,
        quantity=5,
        order_type=OrderType.LIMIT,
        limit_price=3800.0,
    )
    # Limit price overrides the reference price in the notional calc.
    assert order.notional(reference_price=4000.0) == 19000.0
