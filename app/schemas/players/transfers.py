from datetime import date
from typing import Optional, Literal

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerTransferClub(TransfermarktBaseModel):
    id: str
    name: str


class PlayerTransfer(TransfermarktBaseModel):
    id: str
    club_from: PlayerTransferClub
    club_to: PlayerTransferClub
    date: date
    upcoming: bool
    season: str
    market_value: Optional[int]
    fee: Optional[int]
    transfer_type: Literal["permanent", "loan", "end_of_loan", "free_transfer"]


class PlayerTransfers(TransfermarktBaseModel, AuditMixin):
    id: str
    transfers: list[PlayerTransfer]
    youth_clubs: Optional[list[str]]
