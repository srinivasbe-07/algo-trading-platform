"""The strategy interface — the single contract every strategy implements.

In libs/ (shared) because the SAME interface is reused by the backtest engine and
the paper/live engines. A strategy talks only to a Context, so it never knows
whether it runs against historical data, a simulated broker, or a real broker.

Phase 2 adds optional real-time hooks (on_tick, on_order_update) alongside the
bar-driven on_bar, so existing backtest strategies keep working unchanged.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from libs.common.market import Bar
from libs.common.models import OrderStatus


@runtime_checkable
class Context(Protocol):
    """What a strategy is allowed to do. The engine supplies a concrete impl."""

    @property
    def position(self) -> int:
        """Current signed position size (positive = long, negative = short)."""
        ...

    def buy(self, quantity: int) -> None:
        """Queue a market buy of `quantity` units."""
        ...

    def sell(self, quantity: int) -> None:
        """Queue a market sell of `quantity` units."""
        ...


class Strategy(ABC):
    """Base class for all strategies. Override on_bar (and optionally the hooks)."""

    def on_start(self, ctx: Context) -> None:  # noqa: B027 - optional hook
        """Called once before the first bar."""

    @abstractmethod
    def on_bar(self, ctx: Context, bar: Bar) -> None:
        """Called once per bar. Put your trading logic here."""

    def on_tick(self, ctx: Context, symbol: str, price: float) -> None:  # noqa: B027
        """Optional: react to a single real-time price tick (paper/live)."""

    def on_order_update(  # noqa: B027 - optional hook
        self, ctx: Context, order_id: str, status: OrderStatus
    ) -> None:
        """Optional: react to an order's lifecycle change (filled, rejected…)."""

    def on_finish(self, ctx: Context) -> None:  # noqa: B027 - optional hook
        """Called once after the last bar."""
