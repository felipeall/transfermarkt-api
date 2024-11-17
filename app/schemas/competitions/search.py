from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class CompetitionSearchResult(TransfermarktBaseModel):
    id: str
    name: str
    country: str
    clubs: int
    players: int
    total_market_value: Optional[int] = None
    mean_market_value: Optional[int] = None
    continent: Optional[str] = None


class CompetitionSearch(TransfermarktBaseModel, AuditMixin):
    query: str
    page_number: int
    last_page_number: int
    results: list[CompetitionSearchResult]
