import asyncio

from app.services.achievements import group_achievements
from app.tfmkt import TfmktClient


async def get_club_achievements(tfmkt: TfmktClient, club_id: str) -> dict:
    """Club titles, including participations, with the seasons they were won."""
    # the achievement route answers 200 with no data for unknown clubs; the club lookup gives a proper 404
    _, data = await asyncio.gather(tfmkt.club(club_id), tfmkt.club_achievements(club_id))
    return {"id": club_id, "achievements": await group_achievements(tfmkt, data)}
