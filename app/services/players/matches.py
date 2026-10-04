import asyncio
from typing import Optional

from app.tfmkt import TfmktClient
from app.tfmkt.reference import last_page_number

PAGE_SIZE = 50
# upstream participationState -> participation; other values are passed through unchanged
PARTICIPATION = {
    "played": "played",
    "in squad": "onBench",
    "not in squad": "notInSquad",
    "injured": "injured",
    "absent": "absent",
}


async def get_player_matches(
    tfmkt: TfmktClient,
    player_id: str,
    page_number: int,
    season_id: Optional[str] = None,
) -> dict:
    """
    Matches of the player's teams, most recent first, paginated, with the player's part in each.

    Includes matches the player missed (`participation` tells why) and national-team matches. Only past matches are
    available upstream; there is no fixture list.
    """
    performance = (await tfmkt.player_performance_games(player_id))["performance"]
    games = [
        game
        for game in performance
        if season_id is None or str(game["gameInformation"].get("seasonId")) == str(season_id)
    ]
    games.sort(key=lambda game: (game["gameInformation"].get("date") or {}).get("dateTimeUTC") or "", reverse=True)
    page = games[(page_number - 1) * PAGE_SIZE : page_number * PAGE_SIZE]

    competitions, clubs = await asyncio.gather(
        tfmkt.competitions(game["gameInformation"]["competitionId"] for game in page),
        tfmkt.clubs(game["clubsInformation"][side]["clubId"] for game in page for side in ("club", "opponent")),
    )

    def entity(entity_id: str, records: dict) -> dict:
        """`{id, name}` for a referenced club or competition."""
        return {"id": str(entity_id), "name": records.get(str(entity_id), {}).get("name")}

    matches = []
    for game in page:
        info, teams, stats = game["gameInformation"], game["clubsInformation"], game["statistics"]
        state = stats["generalStatistics"].get("participationState")
        cards = stats.get("cardStatistics") or {}
        goals = stats.get("goalStatistics") or {}
        playing_time = stats.get("playingTimeStatistics") or {}
        matches.append({
            "gameId": str(info["gameId"]),
            "date": (info.get("date") or {}).get("dateTimeUTC"),
            "season": (info.get("season") or {}).get("display"),
            "competition": entity(info["competitionId"], competitions),
            "matchDay": info.get("gameDay") or None,
            "club": entity(teams["club"]["clubId"], clubs),
            "opponent": entity(teams["opponent"]["clubId"], clubs),
            "venue": teams["club"].get("venue"),
            "clubGoals": teams["club"].get("goalsTotal"),
            "opponentGoals": teams["opponent"].get("goalsTotal"),
            "participation": PARTICIPATION.get(state, state),
            "isStarting": bool(playing_time.get("isStarting")),
            "minutesPlayed": playing_time.get("playedMinutes") or 0,
            "goals": goals.get("goalsScoredTotal") or 0,
            "assists": goals.get("assists") or 0,
            "yellowCard": bool(cards.get("yellowCard")),
            "secondYellowCard": bool(cards.get("yellowRedCard")),
            "redCard": bool(cards.get("redCard")),
        })

    return {
        "id": player_id,
        "pageNumber": page_number,
        "lastPageNumber": last_page_number(len(games), PAGE_SIZE),
        "matches": matches,
    }
