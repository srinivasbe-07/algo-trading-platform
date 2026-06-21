"""API test for the live-engine service (dry-run)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from live_engine.main import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json()["service"] == "live-engine"


def test_live_run_dry_run_summary() -> None:
    r = client.post("/live/run")
    assert r.status_code == 200
    body = r.json()
    assert body["broker"] == "zerodha-kite"
    assert body["reconciled"] is True
    assert body["orders_submitted"] >= 1
    assert len(body["equity_curve"]) == 300
