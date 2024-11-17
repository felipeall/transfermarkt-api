from datetime import date

from app.schemas.base import AuditMixin, IDMixin, TransfermarktBaseModel


class Injury(TransfermarktBaseModel):
    season: str
    injury: str
    from_date: date
    until_date: date
    days: int
    gamesMissed: int
    gamesMissedClubs: list[str]


class PlayerInjuries(TransfermarktBaseModel, IDMixin, AuditMixin):
    pageNumber: int
    lastPageNumber: int
    injuries: list[Injury]
