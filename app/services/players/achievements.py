import asyncio

from app.services.achievements import group_achievements
from app.tfmkt import TfmktClient


async def get_player_achievements(tfmkt: TfmktClient, player_id: str) -> dict:
    """Titles and individual awards, including participations, runner-up and third places."""
    # the achievement route answers 200 with no data for unknown players; the player lookup gives a proper 404
    _, data = await asyncio.gather(tfmkt.player(player_id), tfmkt.player_achievements(player_id))
    return {"id": player_id, "achievements": await group_achievements(tfmkt, data)}
