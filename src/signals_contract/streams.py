"""Redis Streams helper for publishing/subscribing to typed event streams.

Each stream has a canonical name and a single pydantic type. Producers call
`publish_*` to write; consumers call `subscribe_*` to read with type
deserialization.

Stream catalog (project_trading_stack.md):
    signals:stocks:*       → Signal (existing input from news-consolidator)
    signals:crypto:*       → Signal
    signals:predictions:*  → Signal
    signals:cross-market   → Signal (output from cross-market correlator)
    signals:macro          → MacroEvent
    news:incoming          → freeform news event (not yet typed)
    alphas:active          → Alpha
    positions:open         → Position
    executions:fills       → Fill
    risk:alerts            → KillEvent
    risk:snapshots         → RiskMeter
    sources:scores         → SourceScore

Wire format: each Redis Stream entry has fields { "data": <pydantic JSON> }.
Consumers should use BLOCK with a timeout (typically 5-30s) to avoid CPU spin.

Contract version 0.2.0 (introduced 2026-05-03).
"""
from collections.abc import AsyncIterator
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


# Stream name constants — single source of truth for downstream code.
STREAM_SIGNALS_STOCKS = "signals:stocks"
STREAM_SIGNALS_CRYPTO = "signals:crypto"
STREAM_SIGNALS_PREDICTIONS = "signals:predictions"
STREAM_SIGNALS_CROSS_MARKET = "signals:cross-market"
STREAM_SIGNALS_MACRO = "signals:macro"
STREAM_NEWS_INCOMING = "news:incoming"
STREAM_ALPHAS_ACTIVE = "alphas:active"
STREAM_POSITIONS_OPEN = "positions:open"
STREAM_EXECUTIONS_FILLS = "executions:fills"
STREAM_RISK_ALERTS = "risk:alerts"
STREAM_RISK_SNAPSHOTS = "risk:snapshots"
STREAM_SOURCES_SCORES = "sources:scores"
STREAM_OMS_INTENTS = "oms:intents"


async def publish(redis: object, stream: str, model: BaseModel, maxlen: int = 10_000) -> str:
    """Publish a pydantic model to a Redis Stream.

    Args:
        redis: an `redis.asyncio.Redis` instance.
        stream: stream name (use STREAM_* constants).
        model: any pydantic BaseModel (Alpha, Position, Fill, KillEvent, ...).
        maxlen: stream cap (~ approximate); old entries trimmed beyond this.

    Returns:
        The Redis Stream entry ID (e.g. "1714680000000-0").
    """
    payload = model.model_dump_json()
    return await redis.xadd(  # type: ignore[no-any-return]
        stream,
        {"data": payload},
        maxlen=maxlen,
        approximate=True,
    )


async def subscribe(
    redis: object,
    stream: str,
    model_cls: type[T],
    last_id: str = "$",
    block_ms: int = 5_000,
    count: int = 50,
) -> AsyncIterator[tuple[str, T]]:
    """Subscribe to a Redis Stream, yielding typed pydantic models.

    Args:
        redis: an `redis.asyncio.Redis` instance.
        stream: stream name.
        model_cls: pydantic class to deserialize into.
        last_id: where to start reading. "$" = only new messages from now.
                 "0" = from beginning. Otherwise an entry ID.
        block_ms: BLOCK timeout per XREAD call.
        count: max entries per XREAD batch.

    Yields:
        (entry_id, parsed_model) tuples.
    """
    cursor = last_id
    while True:
        result = await redis.xread(  # type: ignore[attr-defined]
            {stream: cursor},
            block=block_ms,
            count=count,
        )
        if not result:
            continue
        for _stream_name, entries in result:
            for entry_id, fields in entries:
                cursor = entry_id
                raw = fields.get(b"data") or fields.get("data")
                if raw is None:
                    continue
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                yield entry_id, model_cls.model_validate_json(raw)


def stream_for_signal(asset_class: str, asset: str | None = None) -> str:
    """Convenience: build the canonical signals:<class>[:<asset>] stream name."""
    base_map = {
        "crypto": STREAM_SIGNALS_CRYPTO,
        "stocks": STREAM_SIGNALS_STOCKS,
        "predictions": STREAM_SIGNALS_PREDICTIONS,
    }
    base = base_map.get(asset_class, f"signals:{asset_class}")
    if asset:
        return f"{base}:{asset.lower()}"
    return base


__all__ = [
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
    "publish",
    "subscribe",
    "stream_for_signal",
]
