from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class NationalTeam(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None
    appearances: Optional[int] = None
    goals: Optional[int] = None
    shirt_number: Optional[int] = None
    is_captain: Optional[bool] = None
    debut: Optional[date] = None
    last_match: Optional[date] = None
    status: Optional[str] = None


class PlayerNationalCareer(TransfermarktBaseModel, AuditMixin):
    id: str
    national_teams: list[NationalTeam]
