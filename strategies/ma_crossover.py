"""Moving-average crossover strategy.

Go long when the fast moving average crosses above the slow one; exit (and go
flat) when it crosses back below. A classic, simple trend-following rule used
here to exercise the engine end to end.
"""

from __future__ import annotations

from collections import deque

from libs.common.market import Bar
from libs.common.strategy import Context, Strategy


class MACrossover(Strategy):
    def __init__(self, fast: int = 10, slow: int = 20, quantity: int = 50) -> None:
        if fast >= slow:
            raise ValueError("fast window must be shorter than slow window")
        self.fast = fast
        self.slow = slow
        self.quantity = quantity
        self._closes: deque[float] = deque(maxlen=slow)

    def _ma(self, window: int) -> float:
        data = list(self._closes)[-window:]
        return sum(data) / len(data)

    def on_bar(self, ctx: Context, bar: Bar) -> None:
        self._closes.append(bar.close)
        if len(self._closes) < self.slow:
            return  # not enough history yet

        fast_ma = self._ma(self.fast)
        slow_ma = self._ma(self.slow)

        if fast_ma > slow_ma and ctx.position <= 0:
            ctx.buy(self.quantity)
        elif fast_ma < slow_ma and ctx.position > 0:
            ctx.sell(self.quantity)
