from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class AchievementEntity(TransfermarktBaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


class AchievementDetail(TransfermarktBaseModel):
    season: AchievementEntity
    club: Optional[AchievementEntity] = None
    competition: Optional[AchievementEntity] = None


class Achievement(TransfermarktBaseModel):
    title: str
    count: int
    details: list[AchievementDetail]


class Achievements(TransfermarktBaseModel, AuditMixin):
    id: str
    achievements: list[Achievement]
