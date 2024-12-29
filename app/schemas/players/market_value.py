from datetime import date
from typing import Dict, Optional

from pydantic import RootModel

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class MarketValueHistory(TransfermarktBaseModel):
    age: int
    date: date
    club_id: str
    club_name: str
    market_value: Optional[int] = None


class PlayerRanking(RootModel):
    root: Dict[str, int]


class PlayerMarketValue(TransfermarktBaseModel, AuditMixin):
    id: str
    market_value: Optional[int]
    marketValueHistory: list[MarketValueHistory]
    ranking: PlayerRanking
