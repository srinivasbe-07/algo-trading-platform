"""The Risk Engine: a mandatory checkpoint between every signal and any order.

check() runs pre-trade controls and returns an approve/reject decision.
record_fill() updates positions and realised P&L, then runs real-time controls
(daily-loss limit, max drawdown) which can trip the kill-switch automatically.
"""

from __future__ import annotations

import time

from libs.common.models import (
    CanonicalOrder,
    RiskDecision,
    RiskDecisionType,
    Side,
)

from .config import RiskLimits
from .state import RiskState


class RiskEngine:
    def __init__(self, limits: RiskLimits, state: RiskState) -> None:
        self._limits = limits
        self._state = state

    # ---- pre-trade ----------------------------------------------------------
    def check(
        self,
        order: CanonicalOrder,
        reference_price: float,
        strategy: str | None = None,
        now: float | None = None,
    ) -> RiskDecision:
        now = time.time() if now is None else now
        reasons: list[str] = []
        reasons += self._gate_reasons(strategy)
        reasons += self._instrument_reasons(order.symbol)
        reasons += self._size_reasons(order, reference_price)
        if self._exceeds_rate(now):
            reasons.append("order-rate limit exceeded")

        if reasons:
            return RiskDecision(decision=RiskDecisionType.REJECTED, order=order, reasons=reasons)
        self._state.order_times.append(now)
        return RiskDecision(decision=RiskDecisionType.APPROVED, order=order)

    def _gate_reasons(self, strategy: str | None) -> list[str]:
        reasons: list[str] = []
        if self._state.kill_switch:
            reasons.append(f"kill-switch active: {self._state.kill_reason}")
        if strategy is not None and strategy in self._state.paused_strategies:
            reasons.append(f"strategy paused: {strategy}")
        return reasons

    def _instrument_reasons(self, symbol: str) -> list[str]:
        reasons: list[str] = []
        wl = self._limits.instrument_whitelist
        if wl is not None and symbol not in wl:
            reasons.append(f"{symbol} not in whitelist")
        if symbol in self._limits.instrument_blacklist:
            reasons.append(f"{symbol} is blacklisted")
        return reasons

    def _size_reasons(self, order: CanonicalOrder, reference_price: float) -> list[str]:
        reasons: list[str] = []
        if order.quantity > self._limits.max_order_quantity:
            reasons.append("order quantity exceeds limit")
        if order.notional(reference_price) > self._limits.max_order_notional:
            reasons.append("order notional exceeds limit")

        signed = order.quantity if order.side is Side.BUY else -order.quantity
        projected = abs(self._state.position(order.symbol).quantity + signed)
        if projected > self._limits.max_position_quantity:
            reasons.append("projected position exceeds quantity limit")
        if projected * reference_price > self._limits.max_position_notional:
            reasons.append("projected position exceeds notional limit")
        return reasons

    def _exceeds_rate(self, now: float) -> bool:
        window = now - 1.0
        times = self._state.order_times
        while times and times[0] < window:
            times.popleft()
        return len(times) >= self._limits.max_orders_per_second

    # ---- post-fill / real-time ---------------------------------------------
    def record_fill(self, order: CanonicalOrder, fill_price: float, quantity: int) -> None:
        position = self._state.position(order.symbol)
        self._state.realized_pnl += position.apply_fill(order.side, quantity, fill_price)
        self._state.equity_high_water = max(self._state.equity_high_water, self._state.equity)
        self._evaluate_realtime()

    def _evaluate_realtime(self) -> None:
        if self._state.realized_pnl <= -self._limits.daily_loss_limit:
            self.trip_kill_switch("daily loss limit breached")
            return
        peak = self._state.equity_high_water
        if peak > 0:
            drawdown = (peak - self._state.equity) / peak * 100.0
            if drawdown >= self._limits.max_drawdown_pct:
                self.trip_kill_switch("max drawdown breached")

    # ---- controls -----------------------------------------------------------
    def trip_kill_switch(self, reason: str) -> None:
        self._state.kill_switch = True
        self._state.kill_reason = reason

    def reset_kill_switch(self) -> None:
        self._state.kill_switch = False
        self._state.kill_reason = None

    def pause_strategy(self, strategy: str) -> None:
        self._state.paused_strategies.add(strategy)

    def resume_strategy(self, strategy: str) -> None:
        self._state.paused_strategies.discard(strategy)
