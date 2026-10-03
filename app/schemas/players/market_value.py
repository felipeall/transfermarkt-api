from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class MarketValueHistory(TransfermarktBaseModel):
    age: Optional[int] = None
    date: date
    club_id: Optional[str] = None
    club_name: Optional[str] = None
    market_value: Optional[int] = None


class PlayerMarketValue(TransfermarktBaseModel, AuditMixin):
    id: str
    market_value: Optional[int] = None
    market_value_history: list[MarketValueHistory]
    ranking: Optional[dict[str, int]] = None
