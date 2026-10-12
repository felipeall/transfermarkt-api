import asyncio

from transfermarkt_api.exceptions import NotFound
from transfermarkt_api.tfmkt import TfmktClient


async def get_competition_seasons(tfmkt: TfmktClient, competition_id: str) -> dict:
    """Seasons available for a competition, most recent first. Use `id` as `season_id` in other endpoints."""
    data, competitions = await asyncio.gather(
        tfmkt.competition_seasons(competition_id),
        tfmkt.competitions([competition_id]),
    )
    competition = competitions.get(competition_id)
    if competition is None:
        raise NotFound(f"Competition not found: {competition_id}")

    seasons = sorted(data.get("seasons") or [], key=lambda s: s.get("seasonId") or 0, reverse=True)
    return {
        "id": competition_id,
        "name": competition.get("name"),
        "seasons": [
            {
                "id": str(season["seasonId"]),
                "name": (season.get("season") or {}).get("display"),
                "matchDays": season.get("gameDays"),
            }
            for season in seasons
        ],
    }
