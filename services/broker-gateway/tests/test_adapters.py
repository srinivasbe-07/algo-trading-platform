"""Tests covering all broker adapters through the shared base + registry."""

from __future__ import annotations

import pytest
from broker_gateway.adapters import ADAPTERS, build_adapter
from broker_gateway.config import BrokerConfig
from broker_gateway.gateway import BrokerGateway
from libs.common.broker import BrokerError
from libs.common.models import CanonicalOrder, OrderType, Side

ALL_BROKERS = ["zerodha-kite", "fyers", "dhan", "upstox", "delta-exchange"]


def _order(symbol: str = "NIFTY") -> CanonicalOrder:
    return CanonicalOrder(
        symbol=symbol,
        side=Side.BUY,
        quantity=50,
        order_type=OrderType.LIMIT,
        limit_price=20_000.0,
    )


def test_registry_contains_all_brokers() -> None:
    assert set(ADAPTERS) == set(ALL_BROKERS)


@pytest.mark.parametrize("broker", ALL_BROKERS)
def test_dry_run_place_works_for_every_broker(broker: str) -> None:
    adapter = build_adapter(broker, BrokerConfig(dry_run=True))
    adapter.connect()
    result = adapter.place_order(_order())
    assert result.status == "COMPLETE"
    assert adapter.name == broker
    assert adapter.get_positions()[0].quantity == 50


@pytest.mark.parametrize("broker", ALL_BROKERS)
def test_every_broker_works_through_gateway_and_reconciles(broker: str) -> None:
    gw = BrokerGateway(build_adapter(broker, BrokerConfig(dry_run=True)))
    gw.place_order(_order())
    assert gw.reconcile({"NIFTY": 50}) == []
    assert gw.broker_name == broker


@pytest.mark.parametrize("broker", ALL_BROKERS)
def test_live_mode_without_credentials_raises(broker: str) -> None:
    adapter = build_adapter(broker, BrokerConfig(dry_run=False))
    with pytest.raises(BrokerError):
        adapter.connect()


def test_live_mode_with_credentials_is_guarded_not_live() -> None:
    # Even with credentials present, live placement is not enabled yet.
    creds = {"app_id": "x", "access_token": "y"}
    adapter = build_adapter("fyers", BrokerConfig(dry_run=False), creds)
    with pytest.raises(NotImplementedError):
        adapter.connect()


def test_unknown_broker_raises() -> None:
    with pytest.raises(ValueError, match="unknown broker"):
        build_adapter("not-a-broker", BrokerConfig())
