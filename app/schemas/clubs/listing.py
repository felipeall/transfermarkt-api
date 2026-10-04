from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class ListedClub(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None


class ClubListing(TransfermarktBaseModel, AuditMixin):
    country_id: int
    country_name: str
    clubs: list[ListedClub]
