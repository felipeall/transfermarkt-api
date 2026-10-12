from transfermarkt_api.services.achievements import group_achievements
from transfermarkt_api.tfmkt import TfmktClient
from transfermarkt_api.tfmkt.concurrency import gather


async def get_player_achievements(tfmkt: TfmktClient, player_id: str) -> dict:
    """Titles and individual awards, including participations, runner-up and third places."""
    # the achievement route answers 200 with no data for unknown players; the player lookup gives a proper 404
    _, data = await gather(tfmkt.player(player_id), tfmkt.player_achievements(player_id))
    return {"id": player_id, "achievements": await group_achievements(tfmkt, data)}
