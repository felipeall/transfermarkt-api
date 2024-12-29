from app.schemas.base import AuditMixin, TransfermarktBaseModel


class JerseyNumber(TransfermarktBaseModel):
    season: str
    club: str
    jersey_number: int


class PlayerJerseyNumbers(TransfermarktBaseModel, AuditMixin):
    id: str
    jersey_numbers: list[JerseyNumber]
