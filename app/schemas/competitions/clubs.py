from app.schemas.base import AuditMixin, IDMixin, TransfermarktBaseModel


class CompetitionClub(TransfermarktBaseModel, IDMixin):
    name: str


class CompetitionClubs(TransfermarktBaseModel, IDMixin, AuditMixin):
    id: str
    name: str
    season_id: str
    clubs: list[CompetitionClub]
