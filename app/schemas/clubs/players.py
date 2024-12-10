from datetime import date
from typing import Optional

from app.schemas.base import TransfermarktBaseModel


class ClubPlayer(TransfermarktBaseModel):
    name: str
    position: str
    date_of_birth: date
    age: int
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


class ClubPlayers(TransfermarktBaseModel):
    players: list[ClubPlayer]
