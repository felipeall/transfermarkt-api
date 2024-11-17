from app.schemas.base import AuditMixin, TransfermarktBaseModel


class CompetitionClub(TransfermarktBaseModel):
    id: str
    name: str


class CompetitionClubs(TransfermarktBaseModel, AuditMixin):
    id: str
    name: str
    season_id: str
    clubs: list[CompetitionClub]
