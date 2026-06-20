"""The event-driven backtest loop.

Walks bars strictly forward in time. Orders placed after seeing a bar's close
are filled at the NEXT bar's open — so a strategy can never act on information it
would not have had in real time (no look-ahead bias).
"""

from __future__ import annotations

from collections.abc import Iterable

from libs.common.market import Bar
from libs.common.strategy import Strategy

from .broker_sim import SimulatedBroker
from .config import BacktestConfig
from .portfolio import Portfolio


class _Context:
    """Concrete Context handed to the strategy. Queues orders for next-bar fill."""

    def __init__(self, portfolio: Portfolio) -> None:
        self._portfolio = portfolio
        self._pending: list[tuple[str, int]] = []

    @property
    def position(self) -> int:
        return self._portfolio.position

    def buy(self, quantity: int) -> None:
        if quantity > 0:
            self._pending.append(("BUY", quantity))

    def sell(self, quantity: int) -> None:
        if quantity > 0:
            self._pending.append(("SELL", quantity))


class Backtester:
    def __init__(self, config: BacktestConfig | None = None) -> None:
        self._config = config or BacktestConfig()

    def run(self, strategy: Strategy, data: Iterable[Bar]) -> Portfolio:
        portfolio = Portfolio(cash=self._config.initial_cash)
        broker = SimulatedBroker(portfolio, self._config.cost_model)
        ctx = _Context(portfolio)

        strategy.on_start(ctx)
        last_bar: Bar | None = None

        for bar in data:
            # 1. Fill orders placed on the PREVIOUS bar at this bar's open.
            if ctx._pending:
                for side, qty in ctx._pending:
                    broker.fill(bar.timestamp, side, qty, bar.open)
                ctx._pending.clear()

            # 2. Let the strategy react to this bar's close (may queue new orders).
            strategy.on_bar(ctx, bar)

            # 3. Record account value at the close.
            portfolio.record_equity(bar.timestamp, bar.close)
            last_bar = bar

        # Settle any order queued on the final bar at that bar's close.
        if last_bar is not None and ctx._pending:
            for side, qty in ctx._pending:
                broker.fill(last_bar.timestamp, side, qty, last_bar.close)
            ctx._pending.clear()

        strategy.on_finish(ctx)
        return portfolio
