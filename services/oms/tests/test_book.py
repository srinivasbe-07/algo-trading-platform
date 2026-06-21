"""Unit tests for the OMS order book and lifecycle state machine."""

from __future__ import annotations

import pytest
from libs.common.models import CanonicalOrder, OrderStatus, Side
from oms.book import OrderBook, OrderError


def _order(symbol: str = "NIFTY", side: Side = Side.BUY, qty: int = 50) -> CanonicalOrder:
    return CanonicalOrder(symbol=symbol, side=side, quantity=qty)


def test_submit_creates_new_order_with_id() -> None:
    book = OrderBook()
    managed = book.submit(_order())
    assert managed.id
    assert managed.status is OrderStatus.NEW
    assert managed.remaining_quantity == 50


def test_idempotency_returns_same_order() -> None:
    book = OrderBook()
    first = book.submit(_order(), idempotency_key="abc")
    second = book.submit(_order(), idempotency_key="abc")
    assert first.id == second.id
    assert len(book.list_orders()) == 1


def test_full_fill_marks_filled_and_updates_position() -> None:
    book = OrderBook()
    m = book.submit(_order(qty=50))
    book.record_fill(m.id, 50, 20_000.0)
    assert book.get(m.id).status is OrderStatus.FILLED
    assert book.position("NIFTY").quantity == 50


def test_partial_then_full_fill() -> None:
    book = OrderBook()
    m = book.submit(_order(qty=50))
    book.record_fill(m.id, 20, 100.0)
    assert book.get(m.id).status is OrderStatus.PARTIALLY_FILLED
    book.record_fill(m.id, 30, 110.0)
    filled = book.get(m.id)
    assert filled.status is OrderStatus.FILLED
    # Weighted average fill price: (20*100 + 30*110) / 50 = 106
    assert filled.avg_fill_price == 106.0


def test_overfill_is_rejected() -> None:
    book = OrderBook()
    m = book.submit(_order(qty=10))
    with pytest.raises(OrderError):
        book.record_fill(m.id, 20, 100.0)


def test_cannot_fill_cancelled_order() -> None:
    book = OrderBook()
    m = book.submit(_order())
    book.cancel(m.id)
    assert book.get(m.id).status is OrderStatus.CANCELLED
    with pytest.raises(OrderError):
        book.record_fill(m.id, 10, 100.0)


def test_cannot_cancel_filled_order() -> None:
    book = OrderBook()
    m = book.submit(_order(qty=10))
    book.record_fill(m.id, 10, 100.0)
    with pytest.raises(OrderError):
        book.cancel(m.id)


def test_route_transitions_new_to_pending() -> None:
    book = OrderBook()
    m = book.submit(_order())
    book.mark_pending(m.id)
    assert book.get(m.id).status is OrderStatus.PENDING


def test_reject_records_reason() -> None:
    book = OrderBook()
    m = book.submit(_order())
    book.reject(m.id, "risk: blacklisted")
    rejected = book.get(m.id)
    assert rejected.status is OrderStatus.REJECTED
    assert rejected.reject_reason == "risk: blacklisted"


def test_realized_pnl_across_buy_then_sell() -> None:
    book = OrderBook()
    b = book.submit(_order(side=Side.BUY, qty=10))
    book.record_fill(b.id, 10, 100.0)
    s = book.submit(_order(side=Side.SELL, qty=10))
    book.record_fill(s.id, 10, 120.0)
    assert book.position("NIFTY").quantity == 0
    assert book.realized_pnl == 200.0  # (120-100)*10


def test_unknown_order_raises() -> None:
    book = OrderBook()
    with pytest.raises(OrderError):
        book.get("does-not-exist")
