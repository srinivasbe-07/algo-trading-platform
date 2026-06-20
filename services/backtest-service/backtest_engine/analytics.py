"""Performance and risk metrics computed from the equity curve and trade list."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise

from .portfolio import Portfolio, Trade

_TRADING_DAYS = 252


@dataclass(frozen=True)
class Performance:
    initial_equity: float
    final_equity: float
    total_return_pct: float
    cagr_pct: float
    sharpe: float
    sortino: float
    max_drawdown_pct: float
    num_trades: int
    win_rate_pct: float
    profit_factor: float

    def as_text(self) -> str:
        return (
            "Backtest performance\n"
            "--------------------\n"
            f"Initial equity : {self.initial_equity:,.0f}\n"
            f"Final equity   : {self.final_equity:,.0f}\n"
            f"Total return   : {self.total_return_pct:,.2f}%\n"
            f"CAGR           : {self.cagr_pct:,.2f}%\n"
            f"Sharpe ratio   : {self.sharpe:,.2f}\n"
            f"Sortino ratio  : {self.sortino:,.2f}\n"
            f"Max drawdown   : {self.max_drawdown_pct:,.2f}%\n"
            f"Trades         : {self.num_trades}\n"
            f"Win rate       : {self.win_rate_pct:,.2f}%\n"
            f"Profit factor  : {self.profit_factor:,.2f}\n"
        )


def _returns(equity: list[float]) -> list[float]:
    return [(cur - prev) / prev if prev else 0.0 for prev, cur in pairwise(equity)]


def _max_drawdown(equity: list[float]) -> float:
    peak = equity[0]
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, (value - peak) / peak)
    return worst * 100.0


def _risk_ratios(rets: list[float]) -> tuple[float, float]:
    """Annualised Sharpe and Sortino ratios from per-bar returns."""
    n = len(rets)
    if n == 0:
        return 0.0, 0.0
    mean = sum(rets) / n
    std = math.sqrt(sum((r - mean) ** 2 for r in rets) / n)
    downside = [r for r in rets if r < 0]
    dstd = math.sqrt(sum(r * r for r in downside) / len(downside)) if downside else 0.0
    annual = math.sqrt(_TRADING_DAYS)
    sharpe = (mean / std * annual) if std else 0.0
    sortino = (mean / dstd * annual) if dstd else 0.0
    return sharpe, sortino


def _cagr(initial: float, final: float, num_returns: int) -> float:
    years = num_returns / _TRADING_DAYS
    if years <= 0 or initial <= 0:
        return 0.0
    return float((final / initial) ** (1.0 / years) - 1.0) * 100.0


def _trade_stats(trades: list[Trade]) -> tuple[float, float]:
    """Win rate (%) and profit factor over trades that realised P&L."""
    closed = [t for t in trades if t.realized_pnl != 0.0]
    if not closed:
        return 0.0, 0.0
    wins = [t.realized_pnl for t in closed if t.realized_pnl > 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(t.realized_pnl for t in closed if t.realized_pnl < 0))
    win_rate = len(wins) / len(closed) * 100.0
    profit_factor = (gross_profit / gross_loss) if gross_loss else 0.0
    return win_rate, profit_factor


def analyze(portfolio: Portfolio) -> Performance:
    curve = [v for _, v in portfolio.equity_curve]
    if len(curve) < 2:
        initial = curve[0] if curve else 0.0
        return Performance(initial, initial, 0, 0, 0, 0, 0, 0, 0, 0)

    initial, final = curve[0], curve[-1]
    rets = _returns(curve)
    sharpe, sortino = _risk_ratios(rets)
    win_rate, profit_factor = _trade_stats(portfolio.trades)

    return Performance(
        initial_equity=initial,
        final_equity=final,
        total_return_pct=(final - initial) / initial * 100.0,
        cagr_pct=_cagr(initial, final, len(rets)),
        sharpe=sharpe,
        sortino=sortino,
        max_drawdown_pct=_max_drawdown(curve),
        num_trades=len(portfolio.trades),
        win_rate_pct=win_rate,
        profit_factor=profit_factor,
    )
