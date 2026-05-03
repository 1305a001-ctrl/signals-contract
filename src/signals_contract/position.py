"""Position state snapshot — current state of an open position across all venues.

This is a SNAPSHOT contract, not an event. Position state lives in postgres
(trades / poly_positions tables); this model is the wire format for the
`positions:open` Redis stream (one event per state change) and dashboard reads.

Contract version 0.2.0 (introduced 2026-05-03).
"""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from signals_contract._helpers import _parse_json_string


class Position(BaseModel):
    """Snapshot of one open position."""

    id: UUID  # trades.id or poly_positions.id depending on asset_class
    asset_class: Literal["crypto", "stocks", "forex", "predictions"]
    asset: str
    venue: str  # 'okx', 'bybit', 'alpaca', 'oanda', 'ic-markets', 'polymarket'

    strategy_id: UUID
    strategy_slug: str | None = None
    bucket: Literal["fast-intraday", "swing", "conviction", "poly-bet", "hedge"]

    side: Literal["long", "short", "yes", "no"]
        # 'yes'/'no' for predictions; 'long'/'short' for everything else
    qty: float = Field(ge=0)
    notional_usd: float = Field(ge=0)
    entry_price: float | None = None
    current_price: float | None = None

    take_profit_price: float | None = None
    stop_loss_price: float | None = None
    trailing_stop_pct: float | None = None
    time_stop_at: datetime | None = None  # None = no time stop (per new policy)

    unrealized_pnl_usd: float | None = None
    unrealized_pnl_pct: float | None = None
    fees_paid_usd: float = 0.0

    opened_at: datetime
    last_updated_at: datetime
    status: Literal["pending", "open", "partial", "closed"]

    metadata: dict = Field(default_factory=dict)

    _parse_json = field_validator("metadata", mode="before")(_parse_json_string)
