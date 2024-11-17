from app.schemas.base import AuditMixin, IDMixin, TransfermarktBaseModel


class JerseyNumber(TransfermarktBaseModel):
    season: str
    club: str
    jersey_number: int


class PlayerJerseyNumbers(TransfermarktBaseModel, IDMixin, AuditMixin):
    jersey_numbers: list[JerseyNumber]
