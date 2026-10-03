from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class Absence(TransfermarktBaseModel):
    season: Optional[str] = None
    reason: Optional[str] = None
    competition_id: Optional[str] = None
    competition_name: Optional[str] = None
    from_date: Optional[date] = None
    until_date: Optional[date] = None
    days: Optional[int] = None
    games_missed: Optional[int] = None


class PlayerAbsences(TransfermarktBaseModel, AuditMixin):
    id: str
    page_number: int
    last_page_number: int
    absences: list[Absence]
