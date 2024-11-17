from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerStat(TransfermarktBaseModel):
    competition_id: str
    competition_name: str
    season_id: str
    club_id: str
    appearances: Optional[int]
    goals: Optional[int]
    assists: Optional[int]
    yellow_cards: Optional[int]
    red_cards: Optional[int]
    minutes_played: Optional[int]


class PlayerStats(TransfermarktBaseModel, AuditMixin):
    id: str
    stats: list[PlayerStat]
