"""Zerodha Kite adapter — thin subclass of the shared dry-run base."""

from __future__ import annotations

from .base import DryRunBrokerAdapter


class ZerodhaKiteAdapter(DryRunBrokerAdapter):
    name = "zerodha-kite"
    required_credentials = ("api_key", "access_token")
