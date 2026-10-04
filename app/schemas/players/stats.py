from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerStat(TransfermarktBaseModel):
    competition_id: str
    competition_name: Optional[str] = None
    season_id: str
    club_id: str
    appearances: int
    goals: int
    assists: int
    yellow_cards: int
    second_yellow_cards: int
    red_cards: int
    minutes_played: int
    goals_conceded: int
    clean_sheets: int


class PlayerStats(TransfermarktBaseModel, AuditMixin):
    id: str
    stats: list[PlayerStat]
