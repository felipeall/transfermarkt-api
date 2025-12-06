from app.schemas.base import AuditMixin, TransfermarktBaseModel


class CompetitionSeason(TransfermarktBaseModel):
    season_id: str
    season_name: str
    start_year: int
    end_year: int


class CompetitionSeasons(TransfermarktBaseModel, AuditMixin):
    id: str
    name: str
    seasons: list[CompetitionSeason]
