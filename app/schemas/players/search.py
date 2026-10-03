from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerSearchClub(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None


class PlayerSearchResult(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None
    position: Optional[str] = None
    club: Optional[PlayerSearchClub] = None
    age: Optional[int] = None
    nationalities: list[str]
    market_value: Optional[int] = None


class PlayerSearch(TransfermarktBaseModel, AuditMixin):
    query: str
    page_number: int
    last_page_number: int
    results: list[PlayerSearchResult]
