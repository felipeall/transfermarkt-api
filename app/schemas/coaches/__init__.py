from datetime import date
from typing import Optional

from pydantic import HttpUrl

from app.schemas.base import AuditMixin, TransfermarktBaseModel
from app.schemas.players.profile import PlayerPlaceOfBirth


class Coach(TransfermarktBaseModel):
    id: str
    url: Optional[HttpUrl] = None
    name: Optional[str] = None
    name_in_home_country: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    place_of_birth: PlayerPlaceOfBirth
    citizenship: list[str]
    license: Optional[str] = None


class CoachProfile(Coach, AuditMixin):
    pass


class CoachSearch(TransfermarktBaseModel, AuditMixin):
    query: str
    page_number: int
    last_page_number: int
    results: list[Coach]
