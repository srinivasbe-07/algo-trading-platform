"""API test for the paper-trade service."""

from __future__ import annotations

from fastapi.testclient import TestClient
from paper_trade.main import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json()["service"] == "paper-trade"


def test_paper_run_returns_summary() -> None:
    r = client.post("/paper/run")
    assert r.status_code == 200
    body = r.json()
    for key in ("starting_equity", "final_equity", "orders_filled", "return_pct", "equity_curve"):
        assert key in body
    assert body["orders_submitted"] >= 1
    assert len(body["equity_curve"]) == 300
