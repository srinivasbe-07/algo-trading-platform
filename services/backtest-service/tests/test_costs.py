"""Tests for the simulated broker cost model and portfolio bookkeeping."""

from __future__ import annotations

from datetime import datetime

from backtest_engine.broker_sim import SimulatedBroker
from backtest_engine.config import CostModel
from backtest_engine.portfolio import Portfolio


def test_buy_cost_includes_stamp_not_stt() -> None:
    costs = CostModel()
    broker = SimulatedBroker(Portfolio(cash=0.0), costs)
    turnover = 100_000.0
    cost = broker.compute_cost("BUY", turnover)
    # No STT on buy; stamp duty applies.
    expected_brokerage = min(costs.brokerage_per_order, turnover * costs.brokerage_rate)
    expected_txn = turnover * costs.exchange_txn_rate
    expected_gst = (expected_brokerage + expected_txn) * costs.gst_rate
    expected_stamp = turnover * costs.stamp_buy_rate
    expected = expected_brokerage + expected_txn + expected_gst + expected_stamp
    assert cost == expected


def test_sell_cost_includes_stt_not_stamp() -> None:
    costs = CostModel()
    broker = SimulatedBroker(Portfolio(cash=0.0), costs)
    turnover = 100_000.0
    cost = broker.compute_cost("SELL", turnover)
    assert cost > 0
    # Selling should cost more than buying here because STT (0.025%) > stamp (0.003%).
    assert cost > broker.compute_cost("BUY", turnover)


def test_buy_fill_applies_slippage_against_trader() -> None:
    costs = CostModel(slippage_rate=0.01)  # 1% for an easy assertion
    pf = Portfolio(cash=1_000_000.0)
    broker = SimulatedBroker(pf, costs)
    broker.fill(datetime(2024, 1, 1), "BUY", 10, ref_price=100.0)
    # Bought 10 @ 101 (1% slippage up). Position and cash reflect that + costs.
    assert pf.position == 10
    assert pf.trades[0].price == 101.0
    assert pf.cash < 1_000_000.0 - 1010.0  # price paid plus charges


def test_realized_pnl_booked_on_close() -> None:
    pf = Portfolio(cash=1_000_000.0)
    broker = SimulatedBroker(pf, CostModel(slippage_rate=0.0))
    broker.fill(datetime(2024, 1, 1), "BUY", 10, ref_price=100.0)
    broker.fill(datetime(2024, 1, 2), "SELL", 10, ref_price=110.0)
    assert pf.position == 0
    # Gross profit = (110-100)*10 = 100, before costs. Realised pnl is gross.
    assert pf.trades[-1].realized_pnl == 100.0
