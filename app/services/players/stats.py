from collections import Counter

from app.tfmkt import TfmktClient

# Competition type IDs the website's detailed stats table leaves out (national-team matches, including friendlies).
# Mirrors `nationalTeamCompetitions` in the website's player-performance-proxy bundle.
NATIONAL_TEAM_COMPETITION_TYPE_IDS = {11, 17, 19, 20}


async def get_player_stats(tfmkt: TfmktClient, player_id: str) -> dict:
    """
    Aggregate a player's match records into per season, competition and club totals.

    Follows the website's own aggregation of `/player/{id}/performance-game`: appearances count matches with
    participation state `played`, numeric statistics are summed, and each card event counts once. The goalkeeper
    columns follow the website too: `goalsConceded` sums the opponent goals scored while the player was on the pitch,
    and `cleanSheets` counts matches the player played in which the opponent did not score at all. Both are computed
    for every player; the website shows them only for goalkeepers.

    Returns:
        dict: The player ID and one stats entry per (season, competition, club), most recent season first.
    """
    performance = (await tfmkt.player_performance_games(player_id))["performance"]
    games = [
        game
        for game in performance
        if game["gameInformation"]["competitionTypeId"] not in NATIONAL_TEAM_COMPETITION_TYPE_IDS
    ]

    totals: dict[tuple[str, str, str], Counter] = {}
    for game in games:
        info = game["gameInformation"]
        key = (str(info["seasonId"]), info["competitionId"], str(game["clubsInformation"]["club"]["clubId"]))
        total = totals.setdefault(key, Counter())
        stats = game["statistics"]
        if stats["generalStatistics"]["participationState"] != "played":
            continue
        cards = stats["cardStatistics"]
        total["appearances"] += 1
        total["goals"] += stats["goalStatistics"]["goalsScoredTotal"] or 0
        total["assists"] += stats["goalStatistics"]["assists"] or 0
        total["yellowCards"] += 1 if cards.get("yellowCard") else 0
        total["secondYellowCards"] += 1 if cards.get("yellowRedCard") else 0
        total["redCards"] += 1 if cards.get("redCard") else 0
        played_minutes = stats["playingTimeStatistics"]["playedMinutes"] or 0
        total["minutesPlayed"] += played_minutes
        total["goalsConceded"] += stats["goalStatistics"]["opponentGoalsOnThePitch"] or 0
        total["cleanSheets"] += (
            1 if played_minutes and game["clubsInformation"]["club"]["opponentGoalsTotal"] == 0 else 0
        )

    competitions = await tfmkt.competitions(competition_id for _, competition_id, _ in totals)

    return {
        "id": player_id,
        "stats": [
            {
                "competitionId": competition_id,
                "competitionName": competitions.get(competition_id, {}).get("name"),
                "seasonId": season_id,
                "clubId": club_id,
                "appearances": total["appearances"],
                "goals": total["goals"],
                "assists": total["assists"],
                "yellowCards": total["yellowCards"],
                "secondYellowCards": total["secondYellowCards"],
                "redCards": total["redCards"],
                "minutesPlayed": total["minutesPlayed"],
                "goalsConceded": total["goalsConceded"],
                "cleanSheets": total["cleanSheets"],
            }
            for (season_id, competition_id, club_id), total in totals.items()
        ],
    }
