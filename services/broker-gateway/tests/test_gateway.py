"""Tests for the Broker Gateway facade and reconciliation."""

from __future__ import annotations

from broker_gateway.config import BrokerConfig
from broker_gateway.gateway import BrokerGateway
from broker_gateway.kite_adapter import ZerodhaKiteAdapter
from libs.common.models import CanonicalOrder, OrderType, Side


def _gateway() -> BrokerGateway:
    return BrokerGateway(ZerodhaKiteAdapter(BrokerConfig(dry_run=True)))


def _order(qty: int = 50) -> CanonicalOrder:
    return CanonicalOrder(
        symbol="NIFTY",
        side=Side.BUY,
        quantity=qty,
        order_type=OrderType.LIMIT,
        limit_price=20_000.0,
    )


def test_place_via_gateway() -> None:
    gw = _gateway()
    assert gw.broker_name == "zerodha-kite"
    result = gw.place_order(_order())
    assert result.status == "COMPLETE"


def test_reconcile_in_sync() -> None:
    gw = _gateway()
    gw.place_order(_order(50))
    assert gw.reconcile({"NIFTY": 50}) == []


def test_reconcile_detects_drift() -> None:
    gw = _gateway()
    gw.place_order(_order(50))
    discrepancies = gw.reconcile({"NIFTY": 40})
    assert len(discrepancies) == 1
    assert discrepancies[0]["internal"] == 40
    assert discrepancies[0]["broker"] == 50
