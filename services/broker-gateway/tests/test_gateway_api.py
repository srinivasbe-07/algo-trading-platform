"""API tests for the broker-gateway service (dry-run)."""

from __future__ import annotations

from broker_gateway.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json()["service"] == "broker-gateway"


def test_info_reports_dry_run() -> None:
    body = client.get("/broker/info").json()
    assert body["broker"] == "zerodha-kite"
    assert body["dry_run"] is True


def test_place_and_positions() -> None:
    order = {
        "symbol": "NIFTY",
        "side": "BUY",
        "quantity": 50,
        "order_type": "LIMIT",
        "limit_price": 20000.0,
    }
    r = client.post("/broker/orders", json=order)
    assert r.status_code == 200
    assert r.json()["status"] == "COMPLETE"
    assert client.get("/broker/positions").json()["NIFTY"] >= 50


def test_reconcile_endpoint() -> None:
    r = client.post("/broker/reconcile", json={"internal_positions": {"NIFTY": 0}})
    body = r.json()
    assert "in_sync" in body and "discrepancies" in body
