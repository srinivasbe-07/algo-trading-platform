"""The Paper Trading Engine — the orchestrator that brings Phase 2 together.

For each bar it runs the SAME pipeline live trading will use:

    Strategy → (order intent) → OMS.submit → Risk.check
             → approved? OMS.route + PaperBroker.fill + OMS.record_fill + Risk.record_fill
             → rejected? OMS.reject

So a strategy's orders pass real risk checks and are tracked by the real order
book — only the broker is simulated. Orders decided on a bar's close fill at the
NEXT bar's open (no look-ahead), exactly like the backtester.

For Phase 2 (lean) the Risk Engine and OMS are composed in-process; later they
become separate services called over the network without changing this logic.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

from libs.common.market import Bar
from libs.common.models import CanonicalOrder, OrderStatus, Side
from libs.common.strategy import Context, Strategy
from oms.book import OrderBook
from risk_engine.engine import RiskEngine

from .broker import PaperBroker


@dataclass
class PaperResult:
    starting_equity: float
    final_equity: float
    realized_pnl: float
    orders_submitted: int = 0
    orders_filled: int = 0
    orders_rejected: int = 0
    positions: dict[str, int] = field(default_factory=dict)
    equity_curve: list[tuple[datetime, float]] = field(default_factory=list)

    @property
    def return_pct(self) -> float:
        if self.starting_equity == 0:
            return 0.0
        return (self.final_equity - self.starting_equity) / self.starting_equity * 100.0


class _PaperContext:
    """Concrete Context: queues orders for next-bar fill, reports live position."""

    def __init__(self, oms: OrderBook, symbol: str) -> None:
        self._oms = oms
        self._symbol = symbol
        self._pending: list[tuple[Side, int]] = []

    @property
    def position(self) -> int:
        return self._oms.position(self._symbol).quantity

    def buy(self, quantity: int) -> None:
        if quantity > 0:
            self._pending.append((Side.BUY, quantity))

    def sell(self, quantity: int) -> None:
        if quantity > 0:
            self._pending.append((Side.SELL, quantity))

    def take_pending(self) -> list[tuple[Side, int]]:
        pending, self._pending = self._pending, []
        return pending


class PaperTradingEngine:
    def __init__(
        self,
        risk: RiskEngine,
        oms: OrderBook,
        broker: PaperBroker,
        starting_equity: float = 1_000_000.0,
    ) -> None:
        self._risk = risk
        self._oms = oms
        self._broker = broker
        self._starting_equity = starting_equity

    def run(self, strategy: Strategy, bars: Iterable[Bar], symbol: str = "NIFTY") -> PaperResult:
        ctx = _PaperContext(self._oms, symbol)
        result = PaperResult(
            starting_equity=self._starting_equity,
            final_equity=self._starting_equity,
            realized_pnl=0.0,
        )
        cash = self._starting_equity
        strategy_name = type(strategy).__name__
        seq = 0
        strategy.on_start(ctx)

        for bar in bars:
            # Fill orders queued on the previous bar, at THIS bar's open.
            for side, qty in ctx.take_pending():
                seq += 1
                cash += self._process(
                    strategy, ctx, result, symbol, strategy_name, seq, side, qty, bar
                )
            # Strategy reacts to this bar's close (may queue new orders).
            strategy.on_bar(ctx, bar)
            position = self._oms.position(symbol).quantity
            result.equity_curve.append((bar.timestamp, cash + position * bar.close))

        strategy.on_finish(ctx)
        result.final_equity = result.equity_curve[-1][1] if result.equity_curve else cash
        result.realized_pnl = self._oms.realized_pnl
        result.positions = {s: p.quantity for s, p in self._oms.positions().items()}
        return result

    def _process(
        self,
        strategy: Strategy,
        ctx: Context,
        result: PaperResult,
        symbol: str,
        strategy_name: str,
        seq: int,
        side: Side,
        qty: int,
        bar: Bar,
    ) -> float:
        """Run one order through OMS + Risk + broker. Returns the cash delta."""
        order = CanonicalOrder(symbol=symbol, side=side, quantity=qty)
        managed = self._oms.submit(order, idempotency_key=f"{symbol}-{seq}")
        result.orders_submitted += 1

        decision = self._risk.check(
            order, bar.open, strategy=strategy_name, now=bar.timestamp.timestamp()
        )
        if not decision.approved:
            self._oms.reject(managed.id, "; ".join(decision.reasons))
            result.orders_rejected += 1
            strategy.on_order_update(ctx, managed.id, OrderStatus.REJECTED)
            return 0.0

        self._oms.mark_pending(managed.id)
        fill_price, cost = self._broker.simulate_fill(side, qty, bar.open)
        self._oms.record_fill(managed.id, qty, fill_price)
        self._risk.record_fill(order, fill_price, qty)
        result.orders_filled += 1
        strategy.on_order_update(ctx, managed.id, OrderStatus.FILLED)

        signed = qty if side is Side.BUY else -qty
        return -(signed * fill_price) - cost
