from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class Country(TransfermarktBaseModel):
    id: int
    name: str
    fifa_code: Optional[str] = None
    confederation_id: Optional[int] = None
    flag_url: Optional[str] = None
    is_historical: bool


class Countries(TransfermarktBaseModel, AuditMixin):
    countries: list[Country]
