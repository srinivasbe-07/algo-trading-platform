"""Market data types shared across services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Bar:
    """A single OHLCV candle. Immutable so it cannot be tampered with mid-run."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
