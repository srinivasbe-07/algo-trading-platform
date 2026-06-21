"""Risk limits. All configurable so each account/segment can use its own values."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RiskLimits:
    # Per-order
    max_order_quantity: int = 10_000
    max_order_notional: float = 5_000_000.0
    # Per-instrument aggregate position
    max_position_quantity: int = 50_000
    max_position_notional: float = 20_000_000.0
    # Real-time portfolio
    daily_loss_limit: float = 50_000.0  # trip kill-switch if realised loss exceeds
    max_drawdown_pct: float = 10.0  # from intraday equity high-water mark
    # Order-rate guard (SEBI retail threshold is 10 orders/sec)
    max_orders_per_second: int = 10
    # Instrument controls
    instrument_whitelist: frozenset[str] | None = None
    instrument_blacklist: frozenset[str] = field(default_factory=frozenset)
