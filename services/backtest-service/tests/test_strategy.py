"""Tests for the example MA-crossover strategy and the service endpoints."""

from __future__ import annotations

import pytest
from backtest_engine.main import app
from fastapi.testclient import TestClient
from strategies.ma_crossover import MACrossover

client = TestClient(app)


def test_fast_must_be_shorter_than_slow() -> None:
    with pytest.raises(ValueError):
        MACrossover(fast=20, slow=10)


def test_health_endpoint() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "backtest-service"


def test_sample_backtest_endpoint_returns_metrics() -> None:
    r = client.get("/backtest/sample")
    assert r.status_code == 200
    body = r.json()
    # Sanity: the bundled run produces a full metrics payload.
    for key in ("final_equity", "total_return_pct", "sharpe", "num_trades"):
        assert key in body
    assert body["num_trades"] >= 1


def test_detail_endpoint_returns_chart_series() -> None:
    r = client.get("/backtest/detail")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"metrics", "bars", "equity", "trades"}
    assert len(body["bars"]) == 300
    assert len(body["equity"]) == 300
    assert body["bars"][0].keys() >= {"time", "open", "high", "low", "close"}
