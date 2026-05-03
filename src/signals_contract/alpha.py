"""Alpha event — output of the alpha-fusion layer.

Where Signal is INPUT (from news-consolidator), Alpha is OUTPUT (combined +
weighted across many sources, with TTL). Strategies subscribe to the
`alphas:active` Redis stream and act on Alpha events.

Contract version 0.2.0 (introduced 2026-05-03).
"""
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from signals_contract._helpers import _parse_json_string


class ContributingSource(BaseModel):
    """One source's contribution to a fused alpha."""

    source_id: str  # e.g. 'discord:smart-money-tracker', 'cross-market:poly-fed-correlator'
    source_kind: Literal[
        "discord", "telegram", "twitter", "rss",
        "mcp", "on-chain", "cross-market",
        "cot", "fedwatch", "cb-statement",
        "internal-strategy",
    ]
    weight: float = Field(ge=0.0, le=1.0)  # source's score-derived weight at fusion time
    raw_confidence: float = Field(ge=0.0, le=1.0)
    raw_signal_id: UUID | None = None  # for traceability
    metadata: dict = Field(default_factory=dict)

    _parse_json = field_validator("metadata", mode="before")(_parse_json_string)


class Alpha(BaseModel):
    """Fused, weighted alpha for one (asset_class, asset, direction) at point in time.

    Multiple input signals collapse into one Alpha. Strategies decide based on
    `confidence`, `edge_bps`, and the source mix (`contributing_sources`).
    Stale alphas (past `expires_at`) MUST be ignored.
    """

    id: UUID
    created_at: datetime
    expires_at: datetime

    asset_class: Literal["crypto", "stocks", "forex", "predictions"]
    asset: str  # 'BTC-USDT-PERP', 'AAPL', 'EUR/USD', 'poly:fed-rate-cut-feb'
    direction: Literal["long", "short", "watch", "flat"]

    confidence: float = Field(ge=0.0, le=1.0)
    edge_bps: float | None = None  # estimated edge in basis points

    contributing_sources: list[ContributingSource] = Field(default_factory=list)
    reasoning: str | None = None

    superseded_at: datetime | None = None
    superseded_by: UUID | None = None

    metadata: dict = Field(default_factory=dict)

    _parse_json = field_validator("metadata", mode="before")(_parse_json_string)

    def is_live(self, now: datetime | None = None) -> bool:
        """True if this alpha is still actionable (not expired, not superseded)."""
        if self.superseded_at is not None:
            return False
        ref = now or datetime.now(self.expires_at.tzinfo)
        return self.expires_at > ref
