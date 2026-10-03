from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class TableRow(TransfermarktBaseModel):
    position: Optional[int] = None
    previous_position: Optional[int] = None
    club_id: str
    club_name: Optional[str] = None
    matches: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None
    goals_for: Optional[int] = None
    goals_against: Optional[int] = None
    goal_difference: Optional[int] = None
    points: Optional[int] = None
    zone: Optional[str] = None


class Table(TransfermarktBaseModel):
    name: Optional[str] = None
    rows: list[TableRow]


class CompetitionTable(TransfermarktBaseModel, AuditMixin):
    id: str
    name: Optional[str] = None
    season_id: str
    tables: list[Table]
