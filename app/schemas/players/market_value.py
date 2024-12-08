from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, IDMixin, TransfermarktBaseModel


class MarketValueHistory(TransfermarktBaseModel):
    age: int
    date: date
    club_id: str
    club_name: str
    market_value: Optional[int] = None


class PlayerMarketValue(TransfermarktBaseModel, IDMixin, AuditMixin):
    marketValueHistory: list[MarketValueHistory]
