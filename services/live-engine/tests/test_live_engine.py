"""Tests for the Live Trading Engine (Strategy → Risk → OMS → Broker Gateway)."""

from __future__ import annotations

from datetime import datetime, timedelta

from broker_gateway.config import BrokerConfig
from broker_gateway.gateway import BrokerGateway
from broker_gateway.kite_adapter import ZerodhaKiteAdapter
from libs.common.market import Bar
from libs.common.models import OrderStatus
from libs.common.strategy import Context, Strategy
from live_engine.engine import LiveTradingEngine
from oms.book import OrderBook
from risk_engine.config import RiskLimits
from risk_engine.engine import RiskEngine
from risk_engine.state import RiskState


def _bars(closes: list[float]) -> list[Bar]:
    start = datetime(2024, 1, 1)
    out = []
    for i, c in enumerate(closes):
        o = closes[i - 1] if i > 0 else c
        out.append(Bar(start + timedelta(days=i), o, max(o, c), min(o, c), c, 1000))
    return out


class BuyOnce(Strategy):
    def __init__(self, qty: int = 10) -> None:
        self.qty = qty
        self._done = False

    def on_bar(self, ctx: Context, bar: Bar) -> None:
        if not self._done:
            ctx.buy(self.qty)
            self._done = True


def _engine(**limits: object) -> LiveTradingEngine:
    risk = RiskEngine(RiskLimits(**limits), RiskState(starting_equity=1_000_000.0))  # type: ignore[arg-type]
    gateway = BrokerGateway(ZerodhaKiteAdapter(BrokerConfig(dry_run=True)))
    return LiveTradingEngine(risk, OrderBook(), gateway, starting_equity=1_000_000.0)


def test_order_routed_to_broker_and_filled() -> None:
    result = _engine().run(BuyOnce(qty=10), _bars([100.0, 120.0, 130.0]))
    assert result.broker == "zerodha-kite"
    assert result.orders_filled == 1
    assert result.positions["NIFTY"] == 10


def test_oms_and_broker_reconcile_in_sync() -> None:
    result = _engine().run(BuyOnce(qty=10), _bars([100.0, 120.0, 130.0]))
    assert result.reconciled is True
    assert result.discrepancies == []


def test_risk_rejection_means_no_broker_order() -> None:
    result = _engine(max_order_quantity=5).run(BuyOnce(qty=10), _bars([100.0, 120.0]))
    assert result.orders_rejected == 1
    assert result.orders_filled == 0
    assert result.positions.get("NIFTY", 0) == 0
    # Nothing reached the broker, so books are still in sync.
    assert result.reconciled is True


def test_equity_curve_recorded() -> None:
    bars = _bars([100.0, 101.0, 102.0])
    result = _engine().run(BuyOnce(qty=1), bars)
    assert len(result.equity_curve) == len(bars)


class WatchUpdates(Strategy):
    def __init__(self) -> None:
        self.updates: list[OrderStatus] = []
        self._done = False

    def on_bar(self, ctx: Context, bar: Bar) -> None:
        if not self._done:
            ctx.buy(10)
            self._done = True

    def on_order_update(self, ctx: Context, order_id: str, status: OrderStatus) -> None:
        self.updates.append(status)


def test_strategy_notified_of_fill() -> None:
    strat = WatchUpdates()
    _engine().run(strat, _bars([100.0, 120.0]))
    assert OrderStatus.FILLED in strat.updates
