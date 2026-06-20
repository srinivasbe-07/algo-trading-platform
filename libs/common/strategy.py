"""The strategy interface — the single contract every strategy implements.

This is intentionally in libs/ (shared) because the SAME interface is reused by
the backtest engine now and by the paper/live engines later. A strategy talks
only to a Context, so it never knows or cares whether it is running against
historical data (backtest), a simulated broker (paper), or a real broker (live).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from libs.common.market import Bar


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

    def on_finish(self, ctx: Context) -> None:  # noqa: B027 - optional hook
        """Called once after the last bar."""
