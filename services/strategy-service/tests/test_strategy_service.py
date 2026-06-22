"""Tests for the strategy registry and its API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from strategy_service.main import app
from strategy_service.registry import StrategyError, StrategyRegistry, StrategySpec

client = TestClient(app)


def test_registry_create_and_get() -> None:
    reg = StrategyRegistry()
    s = reg.create(StrategySpec(name="MA", fast=5, slow=20, quantity=50))
    assert s.id
    assert reg.get(s.id).name == "MA"
    assert len(reg.list()) == 1


def test_registry_delete_and_missing() -> None:
    reg = StrategyRegistry()
    s = reg.create(StrategySpec(name="x"))
    reg.delete(s.id)
    with pytest.raises(StrategyError):
        reg.get(s.id)
    with pytest.raises(StrategyError):
        reg.delete("nope")


def test_api_create_list_get_delete() -> None:
    created = client.post("/strategies", json={"name": "Nifty MA", "fast": 10, "slow": 20}).json()
    sid = created["id"]
    assert created["name"] == "Nifty MA"
    assert any(s["id"] == sid for s in client.get("/strategies").json())
    assert client.get(f"/strategies/{sid}").json()["name"] == "Nifty MA"
    assert client.delete(f"/strategies/{sid}").status_code == 200
    assert client.get(f"/strategies/{sid}").status_code == 404


def test_health() -> None:
    assert client.get("/health").json()["service"] == "strategy-service"
