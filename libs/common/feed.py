"""Shared CSV bar loader: yields Bars from an OHLCV CSV in time order.

Used by services that need to replay historical/sample data without depending on
one another. (The backtest and paper services predate this and keep their own
loaders; new code should use this shared one.)
"""

from __future__ import annotations

import csv
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from libs.common.market import Bar

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_CSV = REPO_ROOT / "data" / "sample_nifty.csv"


def load_bars(path: str | Path = SAMPLE_CSV) -> Iterator[Bar]:
    with Path(path).open(newline="") as fh:
        for row in csv.DictReader(fh):
            yield Bar(
                timestamp=datetime.fromisoformat(row["date"]),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            )
