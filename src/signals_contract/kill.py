"""KillEvent — the wire format for any halt / kill-switch trigger.

Mirrors the kill_events postgres table. Levels (per project_trading_stack.md):
    0 = pre-trade gate
    1 = per-position SL
    2 = strategy-level
    3 = account-level
    4 = system-level
    5 = manual

Published to Redis stream `risk:alerts` on every event. The OMS, kill-switch
service, dashboard, and pa-agent Telegram all subscribe.

Contract version 0.2.0 (introduced 2026-05-03).
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from signals_contract._helpers import _parse_json_string


class KillEvent(BaseModel):
    """One halt / kill-switch event. Append-only."""

    id: UUID
    triggered_at: datetime

    level: int = Field(ge=0, le=5)
    kind: str
        # e.g. 'manual_halt_all', 'sl_hit', 'daily_dd_breach',
        # 'correlation_cluster', 'broker_api_failure', etc.
    scope: str = "all"
        # 'all', 'strategy:<slug>', 'venue:<slug>', 'position:<uuid>',
        # 'asset_class:<class>'
    actor: str
        # 'telegram:<user>' for manual; 'system' for auto

    reason: str | None = None
    metadata: dict = Field(default_factory=dict)

    cleared_at: datetime | None = None
    cleared_by: str | None = None

    _parse_json = field_validator("metadata", mode="before")(_parse_json_string)

    @property
    def is_active(self) -> bool:
        """True if this halt has not been cleared."""
        return self.cleared_at is None


# Convenience constants for `kind` field — keep in sync with downstream consumers
KIND_MANUAL_HALT_ALL = "manual_halt_all"
KIND_MANUAL_HALT_STRATEGY = "manual_halt_strategy"
KIND_MANUAL_FLAT = "manual_flat"
KIND_MANUAL_RESET_TOMORROW = "manual_reset_tomorrow"
KIND_SL_HIT = "sl_hit"
KIND_TP_HIT = "tp_hit"
KIND_TRAILING_STOP = "trailing_stop"
KIND_DAILY_DD_BREACH = "daily_dd_breach"
KIND_WEEKLY_DD_BREACH = "weekly_dd_breach"
KIND_MONTHLY_DD_BREACH = "monthly_dd_breach"
KIND_TOTAL_DD_BREACH = "total_dd_breach"
KIND_CORRELATION_CLUSTER = "correlation_cluster"
KIND_BROKER_API_FAILURE = "broker_api_failure"
KIND_SYSTEM_HEALTH = "system_health"
KIND_STRATEGY_CONSECUTIVE_LOSSES = "strategy_consecutive_losses"
