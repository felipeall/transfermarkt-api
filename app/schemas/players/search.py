from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerSearchClub(TransfermarktBaseModel):
    id: str
    name: str


class PlayerSearchResult(TransfermarktBaseModel):
    id: str
    name: str
    position: str
    club: PlayerSearchClub
    age: Optional[int]
    nationalities: list[str]
    market_value: Optional[int]


class PlayerSearch(TransfermarktBaseModel, AuditMixin):
    query: str
    pageNumber: int
    lastPageNumber: int
    results: list[PlayerSearchResult]
