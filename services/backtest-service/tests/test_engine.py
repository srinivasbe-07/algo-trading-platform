"""End-to-end engine tests, including the no-look-ahead fill rule."""

from __future__ import annotations

from datetime import datetime, timedelta

from backtest_engine.config import BacktestConfig, CostModel
from backtest_engine.engine import Backtester
from libs.common.market import Bar
from libs.common.strategy import Context, Strategy


def _bars(closes: list[float]) -> list[Bar]:
    start = datetime(2024, 1, 1)
    out = []
    for i, c in enumerate(closes):
        # open == previous close so next-bar-open fills are predictable
        o = closes[i - 1] if i > 0 else c
        out.append(Bar(start + timedelta(days=i), o, max(o, c), min(o, c), c, 1000))
    return out


class BuyOnceStrategy(Strategy):
    """Buys a fixed quantity on the first bar, then holds."""

    def __init__(self, qty: int = 10) -> None:
        self.qty = qty
        self._done = False

    def on_bar(self, ctx: Context, bar: Bar) -> None:
        if not self._done:
            ctx.buy(self.qty)
            self._done = True


def test_order_fills_at_next_bar_open_not_current_close() -> None:
    # Order placed on bar 0 (close 100, with open 100). It must fill at bar 1's
    # OPEN (which equals bar 0 close = 100), proving no look-ahead.
    bars = _bars([100.0, 120.0, 130.0])
    cfg = BacktestConfig(initial_cash=100_000.0, cost_model=CostModel(slippage_rate=0.0))
    pf = Backtester(cfg).run(BuyOnceStrategy(qty=10), bars)
    assert pf.position == 10
    assert pf.trades[0].price == 100.0  # filled at next bar's open, not 120/130


def test_equity_curve_has_one_point_per_bar() -> None:
    bars = _bars([100.0, 101.0, 102.0, 103.0])
    pf = Backtester().run(BuyOnceStrategy(qty=1), bars)
    assert len(pf.equity_curve) == len(bars)


def test_no_trades_when_strategy_inactive() -> None:
    class DoNothing(Strategy):
        def on_bar(self, ctx: Context, bar: Bar) -> None:
            return

    pf = Backtester().run(DoNothing(), _bars([100.0, 101.0]))
    assert pf.position == 0
    assert pf.trades == []
