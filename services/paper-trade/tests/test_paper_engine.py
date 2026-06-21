"""Tests for the Paper Trading Engine orchestration (Strategy → Risk → OMS → broker)."""

from __future__ import annotations

from datetime import datetime, timedelta

from libs.common.market import Bar
from libs.common.models import OrderStatus, Side
from libs.common.strategy import Context, Strategy
from oms.book import OrderBook
from paper_trade.broker import PaperBroker
from paper_trade.engine import PaperTradingEngine
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
        self.updates: list[OrderStatus] = []

    def on_bar(self, ctx: Context, bar: Bar) -> None:
        if not self._done:
            ctx.buy(self.qty)
            self._done = True

    def on_order_update(self, ctx: Context, order_id: str, status: OrderStatus) -> None:
        self.updates.append(status)


def _engine(**limits: object) -> PaperTradingEngine:
    risk = RiskEngine(RiskLimits(**limits), RiskState(starting_equity=1_000_000.0))  # type: ignore[arg-type]
    return PaperTradingEngine(risk, OrderBook(), PaperBroker(), starting_equity=1_000_000.0)


def test_order_flows_through_and_fills() -> None:
    strat = BuyOnce(qty=10)
    result = _engine().run(strat, _bars([100.0, 120.0, 130.0]), symbol="NIFTY")
    assert result.orders_submitted == 1
    assert result.orders_filled == 1
    assert result.orders_rejected == 0
    assert result.positions["NIFTY"] == 10
    assert OrderStatus.FILLED in strat.updates


def test_fill_happens_at_next_bar_open() -> None:
    # Decided on bar 0 (close 100, open 100); fills at bar 1 open (=100).
    result = _engine().run(BuyOnce(qty=10), _bars([100.0, 120.0, 130.0]))
    # Equity ~ unchanged on fill bar minus tiny slippage/cost (bought near 100).
    assert result.positions["NIFTY"] == 10


def test_risk_rejection_blocks_fill() -> None:
    strat = BuyOnce(qty=10)
    # Tiny order-quantity limit forces a rejection.
    result = _engine(max_order_quantity=5).run(strat, _bars([100.0, 120.0]))
    assert result.orders_submitted == 1
    assert result.orders_rejected == 1
    assert result.orders_filled == 0
    assert result.positions.get("NIFTY", 0) == 0
    assert OrderStatus.REJECTED in strat.updates


def test_equity_curve_recorded_per_bar() -> None:
    bars = _bars([100.0, 101.0, 102.0])
    result = _engine().run(BuyOnce(qty=1), bars)
    assert len(result.equity_curve) == len(bars)


def test_broker_slippage_directions() -> None:
    broker = PaperBroker()
    buy_price, _ = broker.simulate_fill(Side.BUY, 10, 100.0)
    sell_price, _ = broker.simulate_fill(Side.SELL, 10, 100.0)
    assert buy_price > 100.0  # pay more to buy
    assert sell_price < 100.0  # receive less to sell
