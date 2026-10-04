from datetime import datetime
from typing import Literal, Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class GameEntity(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None


class GamePlayer(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None
    shirt_number: Optional[int] = None
    position: Optional[str] = None
    is_captain: bool = False


class GameTeamStats(TransfermarktBaseModel):
    possession: Optional[float] = None
    shots: Optional[int] = None
    shots_on_target: Optional[int] = None
    shots_off_target: Optional[int] = None
    shots_blocked: Optional[int] = None
    passes: Optional[int] = None
    accurate_passes: Optional[int] = None
    tackles: Optional[int] = None
    tackles_won: Optional[int] = None
    clearances: Optional[int] = None
    saves: Optional[int] = None
    offsides: Optional[int] = None
    corners: Optional[int] = None
    fouls_committed: Optional[int] = None
    fouls_suffered: Optional[int] = None
    yellow_cards: Optional[int] = None
    second_yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    penalties_won: Optional[int] = None
    penalties_saved: Optional[int] = None
    own_goals: Optional[int] = None


class GameSide(TransfermarktBaseModel):
    id: str
    name: Optional[str] = None
    score: Optional[int] = None
    formation: Optional[str] = None
    coach: Optional[GameEntity] = None
    stats: Optional[GameTeamStats] = None
    starting_lineup: list[GamePlayer]
    substitutes: list[GamePlayer]


class GameScore(TransfermarktBaseModel):
    home: int
    away: int


class GameEvent(TransfermarktBaseModel):
    type: Literal["goal", "card", "substitution"]
    minute: Optional[int] = None
    added_time: Optional[int] = None
    club_id: Optional[str] = None
    player: Optional[GameEntity] = None
    related_player: Optional[GameEntity] = None
    card: Optional[Literal["yellow", "secondYellow", "red"]] = None
    score: Optional[GameScore] = None


class Game(TransfermarktBaseModel, AuditMixin):
    id: str
    url: Optional[str] = None
    competition: GameEntity
    season_id: Optional[str] = None
    season: Optional[str] = None
    match_day: Optional[int] = None
    date: Optional[datetime] = None
    stadium: Optional[GameEntity] = None
    attendance: Optional[int] = None
    home: GameSide
    away: GameSide
    events: list[GameEvent]
