from datetime import datetime
from typing import Literal, Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class PlayerMatchEntity(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None


class PlayerMatch(TransfermarktBaseModel):
    game_id: str
    date: Optional[datetime] = None
    season: Optional[str] = None
    competition: PlayerMatchEntity
    match_day: Optional[int] = None
    club: PlayerMatchEntity
    opponent: PlayerMatchEntity
    venue: Optional[Literal["home", "away", "neutral"]] = None
    club_goals: Optional[int] = None
    opponent_goals: Optional[int] = None
    participation: Optional[str] = None
    is_starting: bool = False
    minutes_played: int = 0
    goals: int = 0
    assists: int = 0
    yellow_card: bool = False
    second_yellow_card: bool = False
    red_card: bool = False


class PlayerMatches(TransfermarktBaseModel, AuditMixin):
    id: str
    page_number: int
    last_page_number: int
    matches: list[PlayerMatch]
