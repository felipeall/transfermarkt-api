from datetime import date
from enum import Enum
from typing import Optional

from pydantic import HttpUrl

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerPlaceOfBirth(TransfermarktBaseModel):
    city: Optional[str]
    country: Optional[str]


class PlayerPosition(TransfermarktBaseModel):
    main: Optional[str]
    other: Optional[list[str]]


class PlayerClub(TransfermarktBaseModel):
    id: Optional[str]
    name: str
    joined: Optional[date]
    contract_expires: Optional[date]
    contract_option: Optional[str]
    # Retired player
    last_club_id: Optional[str]
    last_club_name: Optional[str]
    most_games_for: Optional[str]


class PlayerAgent(TransfermarktBaseModel):
    name: Optional[str]
    url: Optional[str]


class TrainerProfile(TransfermarktBaseModel):
    id: Optional[str]
    url: Optional[str]
    position: Optional[str]


class RelativeProfileTypeEnum(str, Enum):
    PLAYER = "player"
    TRAINER = "trainer"


class Relatives(TransfermarktBaseModel):
    id: str
    url: str
    name: str
    profile_type: RelativeProfileTypeEnum


class PlayerProfile(TransfermarktBaseModel, AuditMixin):
    id: str
    url: HttpUrl
    name: str
    description: str
    full_name: Optional[str]
    name_in_home_country: Optional[str]
    image_url: Optional[HttpUrl]
    date_of_birth: Optional[date]
    place_of_birth: PlayerPlaceOfBirth
    age: Optional[int]
    height: Optional[int]
    citizenship: list[str]
    is_retired: bool
    retired_since: Optional[date]
    position: PlayerPosition
    foot: Optional[str]
    shirt_number: Optional[str]
    club: PlayerClub
    market_value: Optional[int]
    agent: Optional[PlayerAgent]
    outfitter: Optional[str]
    socialMedia: Optional[list[str]]
    trainer_profile: Optional[TrainerProfile]
    relatives: Optional[list[Relatives]]
