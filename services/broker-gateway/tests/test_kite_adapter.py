"""Tests for the Zerodha Kite adapter in dry-run mode (and the live guard)."""

from __future__ import annotations

import pytest
from broker_gateway.config import BrokerConfig
from broker_gateway.kite_adapter import ZerodhaKiteAdapter
from libs.common.broker import BrokerError
from libs.common.models import CanonicalOrder, OrderType, Side


def _adapter() -> ZerodhaKiteAdapter:
    a = ZerodhaKiteAdapter(BrokerConfig(dry_run=True))
    a.connect()
    return a


def _order(side: Side = Side.BUY, qty: int = 50, price: float = 20_000.0) -> CanonicalOrder:
    return CanonicalOrder(
        symbol="NIFTY", side=side, quantity=qty, order_type=OrderType.LIMIT, limit_price=price
    )


def test_dry_run_place_completes_and_updates_position() -> None:
    a = _adapter()
    result = a.place_order(_order())
    assert result.status == "COMPLETE"
    assert result.filled_quantity == 50
    assert a.get_positions()[0].quantity == 50


def test_buy_then_sell_nets_flat() -> None:
    a = _adapter()
    a.place_order(_order(Side.BUY, 50))
    a.place_order(_order(Side.SELL, 50))
    assert a.get_positions()[0].quantity == 0


def test_place_without_connect_raises() -> None:
    a = ZerodhaKiteAdapter(BrokerConfig(dry_run=True))
    with pytest.raises(BrokerError):
        a.place_order(_order())


def test_cancel_completed_order_raises() -> None:
    a = _adapter()
    result = a.place_order(_order())
    with pytest.raises(BrokerError):
        a.cancel_order(result.broker_order_id)


def test_margins_available_in_dry_run() -> None:
    assert _adapter().get_margins().available_cash == 1_000_000.0


def test_live_mode_without_credentials_raises() -> None:
    a = ZerodhaKiteAdapter(BrokerConfig(dry_run=False, api_key=None, access_token=None))
    with pytest.raises(BrokerError):
        a.connect()
