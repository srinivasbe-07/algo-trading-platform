"""CLI runner: backtest the example MA-crossover strategy on the bundled sample.

Run from anywhere:  python services/backtest-service/run_backtest.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parents[2]
# Put the service folder and repo root on the path before local imports.
sys.path[:0] = [str(_THIS.parent), str(_ROOT)]

from backtest_engine.analytics import analyze  # noqa: E402
from backtest_engine.data_feed import CSVDataFeed  # noqa: E402
from backtest_engine.engine import Backtester  # noqa: E402
from strategies.ma_crossover import MACrossover  # noqa: E402

SAMPLE_CSV = _ROOT / "data" / "sample_nifty.csv"


def main() -> None:
    feed = CSVDataFeed(SAMPLE_CSV)
    strategy = MACrossover(fast=10, slow=20, quantity=50)
    portfolio = Backtester().run(strategy, feed)
    print(analyze(portfolio).as_text())


if __name__ == "__main__":
    main()
