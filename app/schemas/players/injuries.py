from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class Injury(TransfermarktBaseModel):
    season: Optional[str] = None
    injury: Optional[str] = None
    from_date: Optional[date] = None
    until_date: Optional[date] = None
    days: Optional[int] = None
    games_missed: Optional[int] = None


class PlayerInjuries(TransfermarktBaseModel, AuditMixin):
    id: str
    page_number: int
    last_page_number: int
    injuries: list[Injury]
