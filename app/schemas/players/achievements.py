from typing import Optional

from app.schemas.base import AuditMixin, TransfermarktBaseModel


class AchievementDetail(TransfermarktBaseModel):
    id: Optional[str] = None
    name: str


class AchievementDetails(TransfermarktBaseModel):
    competition: Optional[AchievementDetail] = None
    season: AchievementDetail
    club: Optional[AchievementDetail] = None


class PlayerAchievement(TransfermarktBaseModel):
    title: str
    count: int
    details: list[AchievementDetails]


class PlayerAchievements(TransfermarktBaseModel, AuditMixin):
    id: str
    achievements: list[PlayerAchievement]
