"""Authentication helpers for the webhook (passphrase + IP allowlist)."""

from __future__ import annotations

import hmac


def passphrase_ok(provided: str, expected: str) -> bool:
    """Constant-time comparison to avoid timing attacks."""
    return hmac.compare_digest(provided, expected)


def ip_allowed(ip: str, allowed: frozenset[str], enabled: bool) -> bool:
    """When the check is disabled, all IPs pass (local dev)."""
    return (not enabled) or ip in allowed
