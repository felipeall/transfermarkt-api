from datetime import date
from typing import Optional

from app.schemas.base import TransfermarktBaseModel


class ClubSquad(TransfermarktBaseModel):
    size: int
    average_age: float
    foreigners: int
    national_team_players: int


class ClubLeague(TransfermarktBaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    country_id: Optional[str] = None
    country_name: Optional[str] = None
    tier: Optional[str] = None


class ClubProfile(TransfermarktBaseModel):
    id: str
    url: str
    name: str
    official_name: Optional[str] = None
    image: str
    legal_form: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_line_3: Optional[str] = None
    tel: Optional[str] = None
    fax: Optional[str] = None
    website: Optional[str] = None
    founded_on: Optional[date] = None
    members: Optional[int] = None
    members_date: Optional[date] = None
    other_sports: Optional[list[str]] = None
    colors: Optional[list[str]] = []
    stadium_name: str
    stadium_seats: int
    current_transfer_record: int
    current_market_value: Optional[int] = None
    confederation: Optional[str] = None
    fifa_world_ranking: Optional[str] = None
    squad: ClubSquad
    league: ClubLeague
    historical_crests: Optional[list[str]] = []
