from datetime import date
from typing import Optional

from pydantic import field_validator

from app.schemas.base import TransfermarktBaseModel, IDMixin, AuditMixin


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
    status: Optional[str] = None


class ClubPlayers(TransfermarktBaseModel):
    players: list[ClubPlayer]


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
    colors: Optional[list[str]] = None
    stadium_name: str
    stadium_seats: int
    current_transfer_record: int
    current_market_value: int
    confederation: Optional[str] = None
    fifa_world_ranking: Optional[str] = None
    squad: ClubSquad
    league: ClubLeague
    historical_crests: Optional[list[str]] = None

    @field_validator("members", mode="before")
    def members_format(cls, value: str):
        return int(value.replace(".", ""))


class ClubSearchResult(TransfermarktBaseModel, IDMixin):
    url: str
    name: str
    country: str
    squad: int
    market_value: Optional[int] = None


class ClubSearch(TransfermarktBaseModel, AuditMixin):
    query: str
    page_number: int
    last_page_number: int
    results: list[ClubSearchResult]
