"""Unit tests for the Risk Engine pre-trade and real-time controls."""

from __future__ import annotations

from libs.common.models import CanonicalOrder, RiskDecisionType, Side
from risk_engine.config import RiskLimits
from risk_engine.engine import RiskEngine
from risk_engine.state import RiskState


def _engine(**limit_overrides: object) -> RiskEngine:
    limits = RiskLimits(**limit_overrides)  # type: ignore[arg-type]
    return RiskEngine(limits, RiskState(starting_equity=1_000_000.0))


def _order(symbol: str = "NIFTY", side: Side = Side.BUY, qty: int = 50) -> CanonicalOrder:
    return CanonicalOrder(symbol=symbol, side=side, quantity=qty)


def test_normal_order_is_approved() -> None:
    decision = _engine().check(_order(), reference_price=20_000.0, now=1000.0)
    assert decision.decision is RiskDecisionType.APPROVED
    assert decision.approved


def test_order_quantity_limit_rejects() -> None:
    eng = _engine(max_order_quantity=10)
    decision = eng.check(_order(qty=50), reference_price=100.0, now=1000.0)
    assert not decision.approved
    assert any("quantity exceeds" in r for r in decision.reasons)


def test_order_notional_limit_rejects() -> None:
    eng = _engine(max_order_notional=1000.0)
    decision = eng.check(_order(qty=50), reference_price=100.0, now=1000.0)  # 5000 notional
    assert not decision.approved
    assert any("notional exceeds" in r for r in decision.reasons)


def test_blacklist_rejects() -> None:
    eng = _engine(instrument_blacklist=frozenset({"NIFTY"}))
    decision = eng.check(_order(), reference_price=20_000.0, now=1000.0)
    assert not decision.approved
    assert any("blacklisted" in r for r in decision.reasons)


def test_whitelist_rejects_unlisted() -> None:
    eng = _engine(instrument_whitelist=frozenset({"BANKNIFTY"}))
    decision = eng.check(_order(symbol="NIFTY"), reference_price=20_000.0, now=1000.0)
    assert not decision.approved
    assert any("whitelist" in r for r in decision.reasons)


def test_projected_position_quantity_limit() -> None:
    eng = _engine(max_position_quantity=60, max_order_quantity=100)
    eng.check(_order(qty=50), reference_price=100.0, now=1000.0)
    eng.record_fill(_order(qty=50), fill_price=100.0, quantity=50)
    # Another 50 would take position to 100 > 60 cap.
    decision = eng.check(_order(qty=50), reference_price=100.0, now=1000.1)
    assert not decision.approved
    assert any("position exceeds quantity" in r for r in decision.reasons)


def test_order_rate_limit() -> None:
    eng = _engine(max_orders_per_second=3)
    for i in range(3):
        assert eng.check(_order(), reference_price=20_000.0, now=1000.0 + i * 0.1).approved
    # 4th within the same second is throttled.
    blocked = eng.check(_order(), reference_price=20_000.0, now=1000.3)
    assert not blocked.approved
    assert any("rate" in r for r in blocked.reasons)


def test_rate_limit_resets_after_one_second() -> None:
    eng = _engine(max_orders_per_second=2)
    eng.check(_order(), reference_price=20_000.0, now=1000.0)
    eng.check(_order(), reference_price=20_000.0, now=1000.5)
    assert not eng.check(_order(), reference_price=20_000.0, now=1000.6).approved
    # A full second later the window has cleared.
    assert eng.check(_order(), reference_price=20_000.0, now=1002.0).approved


def test_kill_switch_blocks_all_orders() -> None:
    eng = _engine()
    eng.trip_kill_switch("manual stop")
    decision = eng.check(_order(), reference_price=20_000.0, now=1000.0)
    assert not decision.approved
    assert any("kill-switch" in r for r in decision.reasons)
    eng.reset_kill_switch()
    assert eng.check(_order(), reference_price=20_000.0, now=1001.0).approved


def test_paused_strategy_blocked() -> None:
    eng = _engine()
    eng.pause_strategy("orb")
    assert not eng.check(_order(), 20_000.0, strategy="orb", now=1000.0).approved
    eng.resume_strategy("orb")
    assert eng.check(_order(), 20_000.0, strategy="orb", now=1001.0).approved


def test_daily_loss_limit_trips_kill_switch() -> None:
    eng = _engine(daily_loss_limit=1000.0, max_order_quantity=1000)
    # Buy 100 @ 100, then sell 100 @ 80 -> realised loss 2000 > 1000 limit.
    eng.record_fill(_order(qty=100), fill_price=100.0, quantity=100)
    eng.record_fill(_order(side=Side.SELL, qty=100), fill_price=80.0, quantity=100)
    blocked = eng.check(_order(), reference_price=100.0, now=1000.0)
    assert not blocked.approved
    assert any("daily loss" in r for r in blocked.reasons)
