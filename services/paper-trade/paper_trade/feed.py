"""Replay market-data feed: streams the bundled sample CSV as if it were live.

In Phase 3 this is replaced by a real broker WebSocket feed; the engine consumes
the same Bar stream either way.
"""

from __future__ import annotations

import csv
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from libs.common.market import Bar

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_CSV = REPO_ROOT / "data" / "sample_nifty.csv"


def replay_csv(path: str | Path = SAMPLE_CSV) -> Iterator[Bar]:
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
