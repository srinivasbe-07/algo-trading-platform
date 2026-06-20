"""Simulated broker: turns order intents into realistic fills with slippage and
India trading costs. In paper/live phases this is swapped for the real Broker
Gateway; the engine and strategies are unchanged.
"""

from __future__ import annotations

from datetime import datetime

from .config import CostModel
from .portfolio import Portfolio


class SimulatedBroker:
    def __init__(self, portfolio: Portfolio, costs: CostModel) -> None:
        self._portfolio = portfolio
        self._costs = costs

    def compute_cost(self, side: str, turnover: float) -> float:
        """Total charges for a single executed order."""
        c = self._costs
        brokerage = min(c.brokerage_per_order, turnover * c.brokerage_rate)
        txn = turnover * c.exchange_txn_rate
        gst = (brokerage + txn) * c.gst_rate
        stt = turnover * c.stt_sell_rate if side == "SELL" else 0.0
        stamp = turnover * c.stamp_buy_rate if side == "BUY" else 0.0
        return brokerage + txn + gst + stt + stamp

    def fill(self, timestamp: datetime, side: str, quantity: int, ref_price: float) -> None:
        """Fill a market order at ref_price adjusted for slippage, then book costs."""
        slip = self._costs.slippage_rate
        # Slippage always works against you: pay more to buy, receive less to sell.
        fill_price = ref_price * (1 + slip) if side == "BUY" else ref_price * (1 - slip)
        turnover = fill_price * quantity
        cost = self.compute_cost(side, turnover)
        self._portfolio.apply_fill(timestamp, side, quantity, fill_price, cost)
