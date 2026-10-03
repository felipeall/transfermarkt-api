import asyncio
from typing import Optional

from fastapi import HTTPException

from app.tfmkt import TfmktClient


async def get_competition_clubs(tfmkt: TfmktClient, competition_id: str, season_id: Optional[str] = None) -> dict:
    """
    List the clubs that took part in a competition season (current season when `season_id` is omitted).

    Club names are the clubs' current names; the membership itself is historical.
    """
    membership, competitions = await asyncio.gather(
        tfmkt.competition_clubs(competition_id, season_id),
        tfmkt.competitions([competition_id]),
    )
    competition = competitions.get(competition_id)
    if competition is None:
        raise HTTPException(status_code=404, detail=f"Competition not found: {competition_id}")

    club_ids = [str(i) for i in membership["clubIds"]]
    clubs = await tfmkt.clubs(club_ids)

    return {
        "id": competition_id,
        "name": competition["name"],
        "seasonId": str(membership["seasonId"]),
        "clubs": [{"id": club_id, "name": clubs.get(club_id, {}).get("name")} for club_id in club_ids],
    }
