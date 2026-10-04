import datetime
from typing import Literal, Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerTransferLeague(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None


class PlayerTransferClub(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None
    country_id: Optional[str] = None
    country_name: Optional[str] = None
    league: Optional[PlayerTransferLeague] = None


class PlayerTransfer(TransfermarktBaseModel):
    id: str
    club_from: PlayerTransferClub
    club_to: PlayerTransferClub
    date: Optional[datetime.date] = None
    upcoming: bool
    transfer_type: Optional[Literal["transfer", "freeTransfer", "internal", "loan", "endOfLoan"]] = None
    season: Optional[str] = None
    market_value: Optional[int] = None
    fee: Optional[int] = None
    age: Optional[int] = None
    contract_until: Optional[datetime.date] = None
    remaining_contract_days: Optional[int] = None


class PlayerTransfers(TransfermarktBaseModel, AuditMixin):
    id: str
    transfers: list[PlayerTransfer]
    youth_clubs: list[str] = []
