from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class ClubSearchResult(TransfermarktBaseModel):
    id: str
    url: Optional[str] = None
    name: Optional[str] = None
    country: Optional[str] = None
    squad: Optional[int] = None
    market_value: Optional[int] = None


class ClubSearch(TransfermarktBaseModel, AuditMixin):
    query: str
    page_number: int
    last_page_number: int
    results: list[ClubSearchResult]
