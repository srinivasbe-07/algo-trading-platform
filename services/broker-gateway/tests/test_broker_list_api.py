"""API test: the gateway lists all available brokers."""

from __future__ import annotations

from broker_gateway.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_broker_list_includes_all_five() -> None:
    brokers = client.get("/broker/list").json()["available_brokers"]
    assert set(brokers) == {"zerodha-kite", "fyers", "dhan", "upstox", "delta-exchange"}
