from typing import Optional

from pydantic import Field

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class ClubPlayer(TransfermarktBaseModel):
    id: str
    name: str
    position: str
    jersey_number: Optional[str] = Field(default=None, alias="jerseyNumber")
    date_of_birth: Optional[str] = None
    age: Optional[str] = None
    nationality: list[str]
    current_club: Optional[str] = None
    height: Optional[str] = None
    foot: Optional[str] = None
    joined_on: Optional[str] = None
    joined: Optional[str] = None
    signed_from: Optional[str] = None
    contract: Optional[str] = None
    market_value: Optional[str] = None
    status: Optional[str] = ""


class ClubPlayers(TransfermarktBaseModel, AuditMixin):
    id: str
    players: list[ClubPlayer]
