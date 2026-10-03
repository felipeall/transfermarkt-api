from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class Season(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None
    match_days: Optional[int] = None


class CompetitionSeasons(TransfermarktBaseModel, AuditMixin):
    id: str
    name: Optional[str] = None
    seasons: list[Season]
