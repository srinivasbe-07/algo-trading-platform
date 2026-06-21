"""Tests for passphrase + IP-allowlist auth helpers."""

from __future__ import annotations

from tradingview_webhook.security import ip_allowed, passphrase_ok


def test_passphrase_match() -> None:
    assert passphrase_ok("secret", "secret")
    assert not passphrase_ok("wrong", "secret")


def test_ip_allow_when_disabled() -> None:
    assert ip_allowed("1.2.3.4", frozenset(), enabled=False)


def test_ip_allowlist_enforced_when_enabled() -> None:
    allowed = frozenset({"52.89.214.238"})
    assert ip_allowed("52.89.214.238", allowed, enabled=True)
    assert not ip_allowed("9.9.9.9", allowed, enabled=True)
