from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class ClubSquad(TransfermarktBaseModel):
    size: Optional[int] = None
    average_age: Optional[float] = None
    foreigners: Optional[int] = None
    national_team_players: Optional[int] = None
    domestic_players: Optional[int] = None
    average_market_value: Optional[int] = None
    acquisition_value: Optional[int] = None
    top_18_players_market_value: Optional[int] = None
    top_18_share_percentage: Optional[float] = None


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


class ClubHistoricalName(TransfermarktBaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    abbreviation: Optional[str] = None
    season_id: Optional[str] = None


class ClubStadium(TransfermarktBaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    capacity: Optional[int] = None
    international_capacity: Optional[int] = None
    website: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    country_id: Optional[str] = None
    country_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    build_year: Optional[int] = None
    renovation_year: Optional[int] = None
    field_length: Optional[int] = None
    field_width: Optional[int] = None
    field_surface: Optional[str] = None
    images: list[str] = []


class ClubProfile(TransfermarktBaseModel, AuditMixin):
    id: str
    url: Optional[str] = None
    name: str
    official_name: Optional[str] = None
    short_name: Optional[str] = None
    abbreviation: Optional[str] = None
    club_code: Optional[str] = None
    image: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_line_3: Optional[str] = None
    colors: list[str] = []
    stadium_name: Optional[str] = None
    stadium_seats: Optional[int] = None
    stadium: Optional[ClubStadium] = None
    current_market_value: Optional[int] = None
    confederation: Optional[str] = None
    coach: Optional[ClubCoach] = None
    squad: ClubSquad
    league: ClubLeague
    historical_crests: list[str] = []
    historical_names: list[ClubHistoricalName] = []
