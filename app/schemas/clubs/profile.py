from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class ClubSquad(TransfermarktBaseModel):
    size: Optional[int] = None
    average_age: Optional[float] = None
    foreigners: Optional[int] = None
    national_team_players: Optional[int] = None


class ClubCoach(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None
    since: Optional[date] = None


class ClubLeague(TransfermarktBaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    country_id: Optional[str] = None
    country_name: Optional[str] = None
    tier: Optional[str] = None


class ClubProfile(TransfermarktBaseModel, AuditMixin):
    id: str
    url: Optional[str] = None
    name: str
    official_name: Optional[str] = None
    image: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_line_3: Optional[str] = None
    colors: list[str] = []
    stadium_name: Optional[str] = None
    stadium_seats: Optional[int] = None
    current_market_value: Optional[int] = None
    confederation: Optional[str] = None
    coach: Optional[ClubCoach] = None
    squad: ClubSquad
    league: ClubLeague
    historical_crests: list[str] = []
