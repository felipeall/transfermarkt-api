import asyncio
from typing import Optional

from fastapi import HTTPException

from app.tfmkt import TfmktClient


async def get_competition_table(tfmkt: TfmktClient, competition_id: str, season_id: Optional[str] = None) -> dict:
    """
    League table for a season (current season when `season_id` is omitted).

    Group-stage competitions return one table per group; knockout-only competitions (cups) return no tables.
    """
    data, competitions = await asyncio.gather(
        tfmkt.competition_table(competition_id, season_id),
        tfmkt.competitions([competition_id]),
    )
    competition = competitions.get(competition_id)
    if competition is None:
        raise HTTPException(status_code=404, detail=f"Competition not found: {competition_id}")

    tables = data.get("tables") or []
    clubs = await tfmkt.clubs(row["clubId"] for table in tables for row in table.get("clubs") or [])
    # upstream `meta.seasonId` always names the current season, even when an older season was requested
    resolved_season = season_id or str(((data.get("meta") or {}).get("seasonId")) or competition.get("currentSeasonId"))

    return {
        "id": competition_id,
        "name": competition.get("name"),
        "seasonId": resolved_season,
        "tables": [
            {
                "name": (table.get("meta") or {}).get("name"),
                "rows": [table_row(row, clubs) for row in table.get("clubs") or []],
            }
            for table in tables
        ],
    }


def table_row(row: dict, clubs: dict) -> dict:
    """Map an upstream table row to the public table row fields."""
    games = row.get("game") or {}
    goals = row.get("goal") or {}
    ranking = row.get("ranking") or {}
    club_id = str(row["clubId"])
    return {
        "position": ranking.get("current"),
        "previousPosition": ranking.get("previous"),
        "clubId": club_id,
        "clubName": clubs.get(club_id, {}).get("name"),
        "matches": games.get("totalCount"),
        "wins": games.get("winCount"),
        "draws": games.get("drawCount"),
        "losses": games.get("lossCount"),
        "goalsFor": goals.get("totalCount"),
        "goalsAgainst": goals.get("concededCount"),
        "goalDifference": goals.get("differenceCount"),
        "points": games.get("points"),
        "zone": (row.get("positioning") or {}).get("description") or None,
    }
