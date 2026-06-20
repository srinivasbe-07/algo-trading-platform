"""Tests for performance metric calculations."""

from __future__ import annotations

from datetime import datetime, timedelta

from backtest_engine.analytics import analyze
from backtest_engine.portfolio import Portfolio


def _portfolio_with_curve(values: list[float]) -> Portfolio:
    pf = Portfolio(cash=values[0])
    base = datetime(2024, 1, 1)
    pf.equity_curve = [(base + timedelta(days=i), v) for i, v in enumerate(values)]
    return pf


def test_total_return_and_drawdown() -> None:
    # Up to 120, down to 90 (drawdown from 120), back to 110.
    perf = analyze(_portfolio_with_curve([100.0, 120.0, 90.0, 110.0]))
    assert round(perf.total_return_pct, 2) == 10.0
    # Max drawdown = (90 - 120) / 120 = -25%
    assert round(perf.max_drawdown_pct, 2) == -25.0


def test_flat_curve_has_zero_metrics() -> None:
    perf = analyze(_portfolio_with_curve([100.0, 100.0, 100.0]))
    assert perf.total_return_pct == 0.0
    assert perf.sharpe == 0.0
    assert perf.max_drawdown_pct == 0.0


def test_single_point_curve_is_safe() -> None:
    perf = analyze(_portfolio_with_curve([100.0]))
    assert perf.final_equity == 100.0
    assert perf.num_trades == 0


def test_report_text_renders() -> None:
    text = analyze(_portfolio_with_curve([100.0, 110.0])).as_text()
    assert "Backtest performance" in text
    assert "CAGR" in text
