"""Canonical Signal pydantic model.

Mirrors news-consolidator INTEGRATION.md. Any field-level change here is a
contract change — bump version, tag, and update consumers' pyproject pins
intentionally.
"""
import json
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class Signal(BaseModel):
    """Inbound signal from Redis (matches news-consolidator INTEGRATION.md).

    For poly signals, `asset` is the Polymarket market slug
    (matches `agent_configs.slug` where `agent_type='poly'`).
    For trading signals, `asset` is the symbol (BTC, NVDA, etc.).
    """

    id: UUID
    strategy_id: UUID
    research_config_id: UUID
    strategy_git_sha: str
    research_config_version: int
    asset: str
    direction: Literal["long", "short", "neutral", "watch"]
    confidence: float = Field(ge=0.0, le=1.0)
    composite_risk_score: float | None = None
    risk_score: dict | None = None
    source_article_ids: list[UUID] = Field(default_factory=list)
    payload: dict = Field(default_factory=dict)
    published_at: datetime

    @field_validator("risk_score", "payload", mode="before")
    @classmethod
    def _parse_json_string(cls, v: Any) -> Any:
        """Tolerate publishers that double-encode JSONB as strings.

        Some upstream paths (e.g. ad-hoc psql republish via NOTIFY, or a
        producer that json.dumps()'d a dict before passing to a JSONB-codec
        column) produce a string where a dict is expected. We try once to
        parse, fall back to passing the string through if it's not JSON.
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v
