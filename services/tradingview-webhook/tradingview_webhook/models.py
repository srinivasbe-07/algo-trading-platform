"""The alert payload contract. We author the alert message in TradingView, so we
define and strictly validate this schema."""

from __future__ import annotations

from libs.common.models import OrderType, Side
from pydantic import BaseModel, Field


class AlertPayload(BaseModel):
    passphrase: str
    symbol: str
    action: Side  # "BUY" / "SELL"
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)  # current price from the alert (e.g. {{close}})
    order_type: OrderType = OrderType.MARKET
    strategy: str | None = None
    alert_id: str | None = None  # optional, used as the OMS idempotency key
