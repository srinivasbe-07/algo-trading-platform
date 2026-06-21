"""API tests for the Risk Engine endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient
from risk_engine.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "risk-engine"


def test_check_endpoint_approves_small_order() -> None:
    body = {
        "order": {"symbol": "NIFTY", "side": "BUY", "quantity": 50},
        "reference_price": 20000.0,
    }
    r = client.post("/risk/check", json=body)
    assert r.status_code == 200
    assert r.json()["decision"] == "APPROVED"


def test_kill_switch_endpoints() -> None:
    assert client.post("/risk/kill", json={"reason": "test"}).status_code == 200
    body = {"order": {"symbol": "NIFTY", "side": "BUY", "quantity": 50}, "reference_price": 20000.0}
    assert client.post("/risk/check", json=body).json()["decision"] == "REJECTED"
    assert client.post("/risk/reset").status_code == 200
    # state endpoint reflects the reset
    assert client.get("/risk/state").json()["kill_switch"] is False


def test_fill_updates_state() -> None:
    client.post("/risk/reset")
    client.post(
        "/risk/fill",
        json={"symbol": "TCS", "side": "BUY", "quantity": 10, "fill_price": 3800.0},
    )
    state = client.get("/risk/state").json()
    assert state["positions"].get("TCS") == 10
