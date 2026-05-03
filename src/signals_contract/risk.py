"""RiskMeter snapshot — periodic P&L + drawdown + exposure at multiple scopes.

Mirrors the risk_ledger postgres table. Published to Redis stream
`risk:snapshots` on every snapshot interval (typically 1 min for intraday,
on-demand for higher periods).

Contract version 0.2.0 (introduced 2026-05-03).
"""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from signals_contract._helpers import _parse_json_string


class RiskMeter(BaseModel):
    """One row of risk_ledger as a wire-format snapshot."""

    id: UUID
    snapshot_at: datetime

    scope: str
        # 'total', 'asset_class:crypto', 'venue:okx', 'strategy:<slug>'
    period: Literal["intraday", "daily", "weekly", "monthly", "total"]

    pnl_usd: float = 0.0
    pnl_pct: float = 0.0

    drawdown_usd: float = 0.0
    drawdown_pct: float = 0.0
    high_water_mark_usd: float | None = None

    open_positions_count: int = 0
    exposure_usd: float = 0.0

    fees_usd: float = 0.0
    slippage_usd: float = 0.0

    trades_opened: int = 0
    trades_closed: int = 0
    trades_won: int = 0
    trades_lost: int = 0

    metadata: dict = Field(default_factory=dict)

    _parse_json = field_validator("metadata", mode="before")(_parse_json_string)

    @property
    def win_rate(self) -> float | None:
        """Win rate if any trades closed in this period; else None."""
        if self.trades_closed == 0:
            return None
        return self.trades_won / self.trades_closed
