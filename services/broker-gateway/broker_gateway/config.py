"""Broker Gateway configuration (env-overridable).

Dry-run is ON by default: orders are validated and tracked locally but NOT sent
to a real broker. Going live = provide that broker's credentials and set
BROKER_DRY_RUN=false. BROKER selects which adapter to bind.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BrokerConfig:
    dry_run: bool = os.environ.get("BROKER_DRY_RUN", "true").lower() != "false"
    broker: str = os.environ.get("BROKER", "zerodha-kite")
