from datetime import date
from typing import Optional

from pydantic import HttpUrl

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class ClubPlayer(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    position: Optional[str] = None
    shirt_number: Optional[int] = None
    is_captain: Optional[bool] = None
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    nationality: list[str]
    current_club: Optional[str] = None
    height: Optional[int] = None
    foot: Optional[str] = None
    joined_on: Optional[date] = None
    signed_from: Optional[str] = None
    contract: Optional[date] = None
    market_value: Optional[int] = None


class ClubPlayers(TransfermarktBaseModel, AuditMixin):
    id: str
    players: list[ClubPlayer]
