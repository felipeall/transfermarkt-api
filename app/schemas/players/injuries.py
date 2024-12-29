from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class Injury(TransfermarktBaseModel):
    season: str
    injury: str
    from_date: date
    until_date: Optional[date]
    days: int
    games_missed: Optional[int]
    games_missed_clubs: list[str]


class PlayerInjuries(TransfermarktBaseModel, AuditMixin):
    id: str
    page_number: int
    last_page_number: int
    injuries: list[Injury]
