"""API tests for the webhook endpoint (auth + processing)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tradingview_webhook.main import app

client = TestClient(app)


def _payload(passphrase: str = "change-me") -> dict[str, object]:
    return {
        "passphrase": passphrase,
        "symbol": "NIFTY",
        "action": "BUY",
        "quantity": 50,
        "price": 20000.0,
    }


def test_health() -> None:
    assert client.get("/health").json()["service"] == "tradingview-webhook"


def test_valid_passphrase_fills() -> None:
    r = client.post("/webhook/tradingview", json=_payload())
    assert r.status_code == 200
    assert r.json()["status"] == "filled"


def test_invalid_passphrase_rejected() -> None:
    r = client.post("/webhook/tradingview", json=_payload(passphrase="nope"))
    assert r.status_code == 403
