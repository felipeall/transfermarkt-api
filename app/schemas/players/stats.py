from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerStat(TransfermarktBaseModel):
    competition_id: str
    competition_name: str
    season_id: str
    club_id: str
    appearances: Optional[int] = 0
    goals: Optional[int] = 0
    assists: Optional[int] = 0
    yellow_cards: Optional[int] = 0
    red_cards: Optional[int] = 0
    minutes_played: Optional[int] = 0


class PlayerStats(TransfermarktBaseModel, AuditMixin):
    id: str
    stats: list[PlayerStat]
