"""MacroEvent — normalized macro events for cross-asset signal generation.

Sources include CFTC COT positioning, CME FedWatch rate expectations,
central bank statements, scheduled economic prints (NFP, CPI, PCE, etc.).
Published to Redis stream `signals:macro` on receipt.

Contract version 0.2.0 (introduced 2026-05-03).
"""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from signals_contract._helpers import _parse_json_string


class MacroEvent(BaseModel):
    """One macro event — past, current, or scheduled future."""

    id: UUID
    received_at: datetime
    event_at: datetime  # when the event itself occurred / is scheduled

    source: str
        # 'cftc-cot', 'cme-fedwatch', 'fomc-statement', 'ecb-statement',
        # 'eia-inventory', 'nfp', 'cpi', 'ppi', 'pce', 'gdp'
    kind: Literal["positioning", "rate-expectation", "statement", "data-release"]

    instrument: str | None = None
        # the asset / instrument the event affects, if scoped:
        # 'EUR/USD', 'CL', 'fed-funds', 'BTC', 'NVDA'

    payload: dict = Field(default_factory=dict)
        # kind-specific normalised data; see each source's normaliser
        # for the schema

    interpretation: Literal[
        "hawkish", "dovish",
        "extreme-long", "extreme-short", "neutral-positioning",
        "in-line", "beat", "miss",
        "scheduled-future",
    ] | None = None
    surprise_score: float | None = None
        # z-score: (actual - consensus) / std(consensus)

    metadata: dict = Field(default_factory=dict)

    _parse_json_payload = field_validator("payload", mode="before")(_parse_json_string)
    _parse_json_meta = field_validator("metadata", mode="before")(_parse_json_string)
