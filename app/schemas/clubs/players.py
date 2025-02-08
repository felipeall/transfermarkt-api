from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class ClubPlayer(TransfermarktBaseModel):
    id: str
    name: str
    position: str
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    nationality: list[str]
    current_club: Optional[str] = None
    height: Optional[int] = None
    foot: Optional[str] = None
    joined_on: Optional[date] = None
    joined: Optional[str] = None
    signed_from: Optional[str] = None
    contract: Optional[date] = None
    market_value: Optional[int] = None
    status: Optional[str] = ""


class ClubPlayers(TransfermarktBaseModel, AuditMixin):
    id: str
    players: list[ClubPlayer]
