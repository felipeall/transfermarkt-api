from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class ClubCompetition(TransfermarktBaseModel):
    id: str
    name: str
    url: Optional[str] = None


class ClubCompetitions(TransfermarktBaseModel, AuditMixin):
    id: str
    season_id: str
    competitions: list[ClubCompetition]
