"""Simulated (paper) broker: realistic fills without risking capital.

Applies slippage (always against the trader) and approximate Indian trading
costs. In live trading this is replaced by the real Broker Gateway; the engine,
strategy, risk, and OMS code are unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass

from libs.common.models import Side


@dataclass(frozen=True)
class PaperBrokerConfig:
    slippage_rate: float = 0.0002  # 0.02% adverse price on fills
    cost_rate: float = 0.0005  # ~0.05% combined charges (approx, configurable)


class PaperBroker:
    def __init__(self, config: PaperBrokerConfig | None = None) -> None:
        self._config = config or PaperBrokerConfig()

    def simulate_fill(
        self, side: Side, quantity: int, reference_price: float
    ) -> tuple[float, float]:
        """Return (fill_price, total_cost) for a market order."""
        slip = self._config.slippage_rate
        fill_price = (
            reference_price * (1 + slip) if side is Side.BUY else reference_price * (1 - slip)
        )
        cost = fill_price * quantity * self._config.cost_rate
        return fill_price, cost
