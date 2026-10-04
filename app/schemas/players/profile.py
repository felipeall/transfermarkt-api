import datetime
from datetime import date
from typing import Literal, Optional

from pydantic import HttpUrl

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerPlaceOfBirth(TransfermarktBaseModel):
    city: Optional[str] = None
    country: Optional[str] = None


class PlayerPosition(TransfermarktBaseModel):
    main: Optional[str] = None
    group: Optional[str] = None
    other: list[str] = []


class PlayerClub(TransfermarktBaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    joined: Optional[date] = None
    is_captain: Optional[bool] = None
    contract_expires: Optional[date] = None
    last_contract_renewal: Optional[date] = None
    contract_option: Optional[str] = None
    last_club_id: Optional[str] = None
    last_club_name: Optional[str] = None


class PlayerNationalTeam(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None
    shirt_number: Optional[str] = None
    is_captain: Optional[bool] = None
    debut: Optional[date] = None


class PlayerDatedValue(TransfermarktBaseModel):
    value: int
    date: Optional[datetime.date] = None


class PlayerMarketValueDetails(TransfermarktBaseModel):
    last_updated: Optional[date] = None
    trend: Optional[Literal["increased", "decreased", "unchanged"]] = None
    previous: Optional[PlayerDatedValue] = None
    highest: Optional[PlayerDatedValue] = None


class PlayerAgent(TransfermarktBaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


class PlayerProfile(TransfermarktBaseModel, AuditMixin):
    id: str
    url: Optional[HttpUrl] = None
    name: str
    full_name: Optional[str] = None
    name_in_home_country: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None
    place_of_birth: PlayerPlaceOfBirth
    age: Optional[int] = None
    height: Optional[int] = None
    citizenship: list[str]
    is_retired: bool
    retired_since: Optional[date] = None
    position: PlayerPosition
    foot: Optional[str] = None
    shirt_number: Optional[str] = None
    club: PlayerClub
    national_team: Optional[PlayerNationalTeam] = None
    market_value: Optional[int] = None
    market_value_details: Optional[PlayerMarketValueDetails] = None
    agent: Optional[PlayerAgent] = None
    outfitter: Optional[str] = None
