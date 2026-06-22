"""Run a backend service on its conventional port (dev helper).

Usage (from the repo root, venv active):
    python run.py risk        # risk-engine    -> http://localhost:8003
    python run.py oms         # order mgmt      -> http://localhost:8004
    python run.py broker      # broker gateway  -> http://localhost:8005
    python run.py backtest    # backtest        -> http://localhost:8000
    python run.py paper       # paper trade     -> http://localhost:8001
    python run.py live        # live engine     -> http://localhost:8002

Ports match frontend/src/api/config.ts. Wires every service folder + the repo
root onto the import path so no PYTHONPATH juggling is needed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SERVICES: dict[str, tuple[str, int]] = {
    "backtest": ("backtest_engine.main:app", 8000),
    "paper": ("paper_trade.main:app", 8001),
    "live": ("live_engine.main:app", 8002),
    "risk": ("risk_engine.main:app", 8003),
    "oms": ("oms.main:app", 8004),
    "broker": ("broker_gateway.main:app", 8005),
}

# All service source folders + repo root (some services import others).
PATHS = [
    str(ROOT / "services" / d)
    for d in (
        "backtest-service",
        "paper-trade",
        "live-engine",
        "risk-engine",
        "oms",
        "broker-gateway",
    )
] + [str(ROOT)]

sys.path[:0] = PATHS
os.environ["PYTHONPATH"] = os.pathsep.join([*PATHS, os.environ.get("PYTHONPATH", "")])


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "backtest"
    if name not in SERVICES:
        raise SystemExit(f"unknown service '{name}'; choose from: {', '.join(SERVICES)}")
    app_path, port = SERVICES[name]

    import uvicorn

    uvicorn.run(app_path, host="127.0.0.1", port=port, reload=True)


if __name__ == "__main__":
    main()
