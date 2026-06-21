"""Broker Gateway configuration (env-overridable).

Dry-run is ON by default: orders are validated and tracked locally but NOT sent
to a real broker. Going live = provide Kite credentials and set BROKER_DRY_RUN=false.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BrokerConfig:
    dry_run: bool = os.environ.get("BROKER_DRY_RUN", "true").lower() != "false"
    api_key: str | None = os.environ.get("KITE_API_KEY")
    api_secret: str | None = os.environ.get("KITE_API_SECRET")
    access_token: str | None = os.environ.get("KITE_ACCESS_TOKEN")
