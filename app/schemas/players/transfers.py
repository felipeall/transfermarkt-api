import datetime
from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerTransferClub(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None


class PlayerTransfer(TransfermarktBaseModel):
    id: str
    club_from: PlayerTransferClub
    club_to: PlayerTransferClub
    date: Optional[datetime.date] = None
    upcoming: bool
    season: Optional[str] = None
    market_value: Optional[int] = None
    fee: Optional[int] = None


class PlayerTransfers(TransfermarktBaseModel, AuditMixin):
    id: str
    transfers: list[PlayerTransfer]
    youth_clubs: list[str] = []
