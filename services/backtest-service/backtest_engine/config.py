"""Backtest configuration and the India cost model defaults."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    """Per-trade costs. Defaults approximate Indian intraday equity charges.

    All rates are fractions of turnover unless noted. These are configurable so
    each segment (equity intraday, delivery, F&O) can use its own numbers.
    """

    brokerage_per_order: float = 20.0  # flat Rs per executed order (cap)
    brokerage_rate: float = 0.0003  # 0.03% of turnover
    stt_sell_rate: float = 0.00025  # securities transaction tax, sell side
    exchange_txn_rate: float = 0.0000345  # exchange transaction charges
    gst_rate: float = 0.18  # GST on (brokerage + txn charges)
    stamp_buy_rate: float = 0.00003  # stamp duty, buy side
    slippage_rate: float = 0.0002  # adverse price move on fills (0.02%)


@dataclass(frozen=True)
class BacktestConfig:
    initial_cash: float = 1_000_000.0
    cost_model: CostModel = CostModel()
