"""Receiver configuration (env-overridable).

TradingView can only send a URL + a message body — no custom auth headers — so we
authenticate with a shared passphrase inside the payload plus an IP allowlist of
TradingView's published webhook server IPs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# TradingView's published webhook source IPs (verify against their current docs
# before enabling in production; they can change).
TRADINGVIEW_IPS: frozenset[str] = frozenset(
    {"52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"}
)


@dataclass(frozen=True)
class WebhookConfig:
    passphrase: str = os.environ.get("TVHOOK_PASSPHRASE", "change-me")
    # IP check is off by default for local dev; enable it (and verify the IP list)
    # in production via TVHOOK_IP_CHECK=true.
    ip_check_enabled: bool = os.environ.get("TVHOOK_IP_CHECK", "false").lower() == "true"
    allowed_ips: frozenset[str] = field(default_factory=lambda: TRADINGVIEW_IPS)
