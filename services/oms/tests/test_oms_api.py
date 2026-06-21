"""API tests for the OMS endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient
from oms.main import app

client = TestClient(app)


def _submit(qty: int = 50, key: str | None = None) -> str:
    body = {"order": {"symbol": "NIFTY", "side": "BUY", "quantity": qty}}
    if key is not None:
        body["idempotency_key"] = key
    return client.post("/orders", json=body).json()["id"]


def test_health() -> None:
    assert client.get("/health").json()["service"] == "oms"


def test_submit_and_fetch() -> None:
    oid = _submit()
    r = client.get(f"/orders/{oid}")
    assert r.status_code == 200
    assert r.json()["status"] == "NEW"


def test_fill_flow_updates_positions() -> None:
    oid = _submit(qty=10, key="api-fill-1")
    client.post(f"/orders/{oid}/route")
    r = client.post(f"/orders/{oid}/fills", json={"quantity": 10, "price": 100.0})
    assert r.json()["status"] == "FILLED"
    assert client.get("/positions").json()["positions"]["NIFTY"] >= 10


def test_illegal_transition_returns_409() -> None:
    oid = _submit(qty=10, key="api-cancel-1")
    client.post(f"/orders/{oid}/fills", json={"quantity": 10, "price": 100.0})
    # Cancelling a filled order is illegal.
    assert client.post(f"/orders/{oid}/cancel").status_code == 409


def test_unknown_order_returns_404() -> None:
    assert client.get("/orders/nope").status_code == 404
