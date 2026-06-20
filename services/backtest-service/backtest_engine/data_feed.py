"""Historical data feeds. The engine only knows the iterator contract, so the
source (CSV now, broker API later) can change without touching the engine.
"""

from __future__ import annotations

import csv
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from libs.common.market import Bar


class CSVDataFeed:
    """Reads OHLCV bars from a CSV with columns: date,open,high,low,close,volume."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def __iter__(self) -> Iterator[Bar]:
        with self._path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                yield Bar(
                    timestamp=datetime.fromisoformat(row["date"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                )
