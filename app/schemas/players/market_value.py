from datetime import date
from typing import Dict, Optional

from pydantic import RootModel, model_validator

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class MarketValueHistory(TransfermarktBaseModel):
    age: int
    date: date
    club_id: str
    club_name: str
    market_value: Optional[int] = None


class PlayerRanking(RootModel):
    root: Dict[str, int]

    @model_validator(mode="before")
    def parse_ranking_values(cls, v: Dict[str, str]) -> Dict[str, int]:
        """Parse the ranking values from string to int.

        E.g.: {"Worldwide": "1.234"} -> {"Worldwide": 1234}
        """
        return {k: int(v.replace(".", "")) for k, v in v.items()}


class PlayerMarketValue(TransfermarktBaseModel, AuditMixin):
    id: str
    market_value: Optional[int]
    marketValueHistory: list[MarketValueHistory]
    ranking: PlayerRanking
