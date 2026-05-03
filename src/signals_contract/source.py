"""SourceScore — per-source rolling Sharpe / win-rate / weight.

Mirrors the source_scores postgres table. Updated nightly by the alpha-scorer
on ai-staging. The `weight` is multiplied into raw confidences when the
fusion layer combines signals into Alphas.

Contract version 0.2.0 (introduced 2026-05-03).
"""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from signals_contract._helpers import _parse_json_string


class SourceScore(BaseModel):
    """One snapshot of a source's recent performance."""

    id: UUID
    snapshot_at: datetime

    source_id: str
    source_kind: Literal[
        "discord", "telegram", "twitter", "rss",
        "mcp", "on-chain", "cross-market",
        "cot", "fedwatch", "cb-statement",
        "internal-strategy",
    ]

    window_days: int = Field(gt=0)  # 7, 30, 90 — track multiple windows

    signals_emitted: int = 0
    signals_actionable: int = 0
    signals_traded: int = 0
    signals_won: int = 0
    signals_lost: int = 0

    rolling_sharpe: float | None = None
    rolling_win_rate: float | None = None
    rolling_avg_edge_bps: float | None = None
    rolling_pnl_usd: float | None = None

    weight: float = Field(default=0.0, ge=0.0, le=1.0)
        # 0.0 = effectively muted; 1.0 = full weight

    metadata: dict = Field(default_factory=dict)

    _parse_json = field_validator("metadata", mode="before")(_parse_json_string)
