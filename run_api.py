"""Dev launcher for the backtest API.

Run from the repo root:  python run_api.py
Then open http://localhost:8000/docs  (or the frontend at :5173).

This wires both the service folder (for `backtest_engine`) and the repo root
(for `libs` and `strategies`) onto the import path, so you do not need to set
PYTHONPATH by hand.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATHS = [str(ROOT / "services" / "backtest-service"), str(ROOT)]

# Make imports work in this process AND in uvicorn's reload subprocess.
sys.path[:0] = PATHS
os.environ["PYTHONPATH"] = os.pathsep.join([*PATHS, os.environ.get("PYTHONPATH", "")])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backtest_engine.main:app", host="127.0.0.1", port=8000, reload=True)
