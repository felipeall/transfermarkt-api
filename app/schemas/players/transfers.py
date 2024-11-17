from datetime import date
from typing import Optional

from app.schemas.base import AuditMixin, IDMixin, TransfermarktBaseModel


class PlayerTransferClub(TransfermarktBaseModel):
    id: str
    name: str


class PlayerTransfer(TransfermarktBaseModel, IDMixin):
    club_from: PlayerTransferClub
    club_to: PlayerTransferClub
    date: date
    upcoming: bool
    season: str
    market_value: Optional[int]
    fee: str


class PlayerTransfers(TransfermarktBaseModel, AuditMixin, IDMixin):
    transfers: list[PlayerTransfer]
    youth_clubs: list[str]
