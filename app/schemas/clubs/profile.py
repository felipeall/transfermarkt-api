from datetime import date
from typing import Optional

from app.schemas.base import TransfermarktBaseModel


class ClubSquad(TransfermarktBaseModel):
    size: int
    average_age: float
    foreigners: int
    national_team_players: int


class ClubLeague(TransfermarktBaseModel):
    id: str
    name: str
    country_id: str
    country_name: str
    tier: str


class ClubProfile(TransfermarktBaseModel):
    id: str
    url: str
    name: str
    official_name: str
    image: str
    legal_form: Optional[str] = None
    address_line_1: str
    address_line_2: str
    address_line_3: str
    tel: str
    fax: str
    website: str
    founded_on: date
    members: Optional[int] = None
    members_date: Optional[date] = None
    other_sports: Optional[list[str]] = None
    colors: Optional[list[str]] = []
    stadium_name: str
    stadium_seats: int
    current_transfer_record: int
    current_market_value: int
    confederation: Optional[str] = None
    fifa_world_ranking: Optional[str] = None
    squad: ClubSquad
    league: ClubLeague
    historical_crests: Optional[list[str]] = []
