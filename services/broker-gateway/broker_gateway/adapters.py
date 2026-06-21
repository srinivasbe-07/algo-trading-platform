"""All broker adapters + a registry to pick one by name.

Every adapter is a thin subclass of DryRunBrokerAdapter: it just declares its
name and the credentials its live mode will need. Dry-run behaviour is shared.
"""

from __future__ import annotations

from .base import DryRunBrokerAdapter
from .config import BrokerConfig
from .kite_adapter import ZerodhaKiteAdapter


class FyersAdapter(DryRunBrokerAdapter):
    name = "fyers"
    required_credentials = ("app_id", "access_token")


class DhanAdapter(DryRunBrokerAdapter):
    name = "dhan"
    required_credentials = ("client_id", "access_token")


class UpstoxAdapter(DryRunBrokerAdapter):
    name = "upstox"
    required_credentials = ("api_key", "access_token")


class DeltaExchangeAdapter(DryRunBrokerAdapter):
    name = "delta-exchange"  # crypto derivatives (India)
    required_credentials = ("api_key", "api_secret")


ADAPTERS: dict[str, type[DryRunBrokerAdapter]] = {
    cls.name: cls
    for cls in (
        ZerodhaKiteAdapter,
        FyersAdapter,
        DhanAdapter,
        UpstoxAdapter,
        DeltaExchangeAdapter,
    )
}


def build_adapter(
    name: str, config: BrokerConfig | None = None, credentials: dict[str, str] | None = None
) -> DryRunBrokerAdapter:
    if name not in ADAPTERS:
        raise ValueError(f"unknown broker '{name}'; available: {', '.join(sorted(ADAPTERS))}")
    return ADAPTERS[name](config, credentials)
