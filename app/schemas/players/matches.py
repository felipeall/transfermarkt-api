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
    shirt_number: Optional[int] = None
    is_captain: bool = False
    position: Optional[str] = None
    is_starting: bool = False
    substituted_in_minute: Optional[int] = None
    substituted_out_minute: Optional[int] = None
    minutes_played: int = 0
    team_points: Optional[int] = None
    goals: int = 0
    assists: int = 0
    yellow_card: bool = False
    second_yellow_card: bool = False
    red_card: bool = False
    own_goals: Optional[int] = None
    penalty_goals: Optional[int] = None
    penalties_missed: Optional[int] = None
    penalties_saved: Optional[int] = None
    shots: Optional[int] = None
    shots_on_target: Optional[int] = None
    passes: Optional[int] = None
    accurate_passes: Optional[int] = None
    tackles: Optional[int] = None
    tackles_won: Optional[int] = None
    fouls_committed: Optional[int] = None
    fouls_suffered: Optional[int] = None
    offsides: Optional[int] = None


class PlayerMatches(TransfermarktBaseModel, AuditMixin):
    id: str
    page_number: int
    last_page_number: int
    matches: list[PlayerMatch]
