"""Fill confirmation — emitted by OMS after a broker reports an order fill.

Published to Redis stream `executions:fills` so risk ledger, observability,
and dashboard can react in real-time. Persisted into trades / poly_positions
tables and oms_intents.fill_* fields by the OMS.

Contract version 0.2.0 (introduced 2026-05-03).
"""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from signals_contract._helpers import _parse_json_string


class Fill(BaseModel):
    """A broker-confirmed fill against an order intent."""

    id: UUID  # internal fill id
    intent_id: UUID  # FK to oms_intents.id
    venue: str
    broker_order_id: str
    broker_fill_id: str | None = None
        # some brokers split a single intent into multiple fill events

    asset_class: Literal["crypto", "stocks", "forex", "predictions"]
    asset: str
    side: Literal["buy", "sell"]

    qty: float = Field(gt=0)
    price: float = Field(gt=0)
    notional_usd: float = Field(gt=0)

    fees_usd: float = Field(ge=0)
    rebate_usd: float = Field(default=0.0, ge=0)
        # for maker-rebate venues; tracked separately so net cost is honest

    is_maker: bool | None = None
    liquidity_flag: Literal["maker", "taker", "unknown"] = "unknown"

    filled_at: datetime
    received_at: datetime  # when WE saw the fill confirmation

    metadata: dict = Field(default_factory=dict)

    _parse_json = field_validator("metadata", mode="before")(_parse_json_string)

    @property
    def net_fees_usd(self) -> float:
        """Fees minus rebates. Strategy P&L should net against this."""
        return self.fees_usd - self.rebate_usd
