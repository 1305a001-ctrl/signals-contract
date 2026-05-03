"""Shared signal contract for the2357.com stack.

The `Signal` model is the canonical wire format produced by news-consolidator
on Redis channels (`signals:trading`, `signals:poly`, `signals:critical`,
`signals:new`) and consumed by trading-agent, poly-agent, and pa-agent.

v0.2.0 (2026-05-03): adds Alpha, Position, Fill, KillEvent, RiskMeter,
SourceScore, MacroEvent + Redis Streams helpers, in support of the multi-
machine trading stack pivot. See `docs/streams.md` and project_trading_stack.md.

Versioning policy (semver):
- PATCH: docs, validators, no field changes.
- MINOR: new optional field, or new event type. Existing types unchanged.
- MAJOR: any breaking shape change to existing types. Pin to a specific tag
  in consumers' pyproject.toml so a major bump can't silently land on next
  image build.

Producers MUST emit fields in the canonical schema. Consumers MUST tolerate
unknown future fields (pydantic's default extra='ignore' covers this).
"""
from signals_contract.alpha import Alpha, ContributingSource
from signals_contract.fill import Fill
from signals_contract.kill import KillEvent
from signals_contract.macro import MacroEvent
from signals_contract.position import Position
from signals_contract.risk import RiskMeter
from signals_contract.signal import Signal
from signals_contract.source import SourceScore
from signals_contract.streams import (
    STREAM_ALPHAS_ACTIVE,
    STREAM_EXECUTIONS_FILLS,
    STREAM_NEWS_INCOMING,
    STREAM_OMS_INTENTS,
    STREAM_POSITIONS_OPEN,
    STREAM_RISK_ALERTS,
    STREAM_RISK_SNAPSHOTS,
    STREAM_SIGNALS_CROSS_MARKET,
    STREAM_SIGNALS_CRYPTO,
    STREAM_SIGNALS_MACRO,
    STREAM_SIGNALS_PREDICTIONS,
    STREAM_SIGNALS_STOCKS,
    STREAM_SOURCES_SCORES,
    publish,
    stream_for_signal,
    subscribe,
)

__all__ = [
    "Signal",
    "Alpha",
    "ContributingSource",
    "Position",
    "Fill",
    "KillEvent",
    "RiskMeter",
    "SourceScore",
    "MacroEvent",
    "publish",
    "subscribe",
    "stream_for_signal",
    "STREAM_SIGNALS_STOCKS",
    "STREAM_SIGNALS_CRYPTO",
    "STREAM_SIGNALS_PREDICTIONS",
    "STREAM_SIGNALS_CROSS_MARKET",
    "STREAM_SIGNALS_MACRO",
    "STREAM_NEWS_INCOMING",
    "STREAM_ALPHAS_ACTIVE",
    "STREAM_POSITIONS_OPEN",
    "STREAM_EXECUTIONS_FILLS",
    "STREAM_RISK_ALERTS",
    "STREAM_RISK_SNAPSHOTS",
    "STREAM_SOURCES_SCORES",
    "STREAM_OMS_INTENTS",
]
__version__ = "0.2.0"
