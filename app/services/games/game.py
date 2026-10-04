import asyncio
from typing import Optional

from app.tfmkt import TfmktClient
from app.tfmkt.reference import full_url

EVENT_TYPES = {"GOAL": "goal", "CARD": "card", "SUBSTITUTE": "substitution"}
# team stat -> (clubStatistics group, upstream field)
TEAM_STATS = {
    "possession": ("gameStatistics", "possessionPercentage"),
    "shots": ("goalStatistics", "totalShotAttempts"),
    "shotsOnTarget": ("goalStatistics", "onTargetShotAttempts"),
    "shotsOffTarget": ("goalStatistics", "offTargetShotAttempts"),
    "shotsBlocked": ("goalStatistics", "blockedShotAttempts"),
    "passes": ("passingStatistics", "totalPasses"),
    "accuratePasses": ("passingStatistics", "accuratePasses"),
    "tackles": ("defensiveStatistics", "totalTackles"),
    "tacklesWon": ("defensiveStatistics", "successfulTackles"),
    "clearances": ("defensiveStatistics", "clearances"),
    "saves": ("defensiveStatistics", "saves"),
    "offsides": ("defensiveStatistics", "offsides"),
    "corners": ("setPieceStatistics", "cornersTaken"),
    "foulsCommitted": ("penaltyStatistics", "freeKicksConcededFromFouls"),
    "foulsSuffered": ("penaltyStatistics", "freeKicksWonFromFouls"),
    "yellowCards": ("gameStatistics", "yellowCards"),
    "secondYellowCards": ("gameStatistics", "secondYellowCards"),
    "redCards": ("gameStatistics", "redCards"),
    "penaltiesWon": ("penaltyStatistics", "penaltiesWon"),
    "penaltiesSaved": ("penaltyStatistics", "penaltiesSaved"),
    "ownGoals": ("penaltyStatistics", "ownGoals"),
}


async def get_game(tfmkt: TfmktClient, game_id: str) -> dict:
    """
    A match with both lineups, coaches, score and events.

    `stats` holds team statistics (possession, shots, passes, ...) when upstream recorded them, mostly for recent
    matches in major competitions; otherwise it is null. Events are goals, cards and substitutions in match order.
    For a goal, `relatedPlayer` is the assist; for a substitution, `player` goes off and `relatedPlayer` comes on.
    """
    game = await tfmkt.game(game_id)
    base = game.get("baseDetails") or {}
    sides = {"home": game.get("homeClub") or {}, "away": game.get("awayClub") or {}}
    actions = [action for action in game.get("actions") or [] if action.get("type") in EVENT_TYPES]
    lineups = {
        name: {group: (side.get("lineup") or {}).get(group) or [] for group in ("players", "substitutes")}
        for name, side in sides.items()
    }
    player_ids = [p["id"] for lineup in lineups.values() for group in lineup.values() for p in group] + [
        action[key] for action in actions for key in ("activePlayerId", "passivePlayerId") if action.get(key)
    ]
    stadium_id = base.get("stadiumId")

    players, clubs, coaches, stadium = await asyncio.gather(
        tfmkt.players(player_ids),
        tfmkt.clubs(side.get("clubId") for side in sides.values()),
        tfmkt.coaches(side.get("coachId") for side in sides.values()),
        tfmkt.stadium(stadium_id) if stadium_id else asyncio.sleep(0),
    )

    def entity(entity_id: Optional[str], records: dict) -> Optional[dict]:
        """`{id, name}` for a referenced player, club or coach, or None when there is no ID."""
        if not entity_id:
            return None
        return {"id": str(entity_id), "name": records.get(str(entity_id), {}).get("name")}

    def lineup_player(player: dict) -> dict:
        """A lineup entry with the player's name."""
        return {
            **entity(player["id"], players),
            "shirtNumber": player.get("shirtNumber"),
            "position": (player.get("position") or {}).get("name"),
            "isCaptain": bool(player.get("isCaptain")),
        }

    score = game.get("score") or {}
    competition = base.get("competition") or {}
    date = base.get("date") or {}

    return {
        "id": str(game.get("id") or game_id),
        "url": full_url(game.get("relativeUrl")),
        "competition": {"id": base.get("competitionId"), "name": competition.get("name")},
        "seasonId": str(base["seasonId"]) if base.get("seasonId") is not None else None,
        "season": (base.get("season") or {}).get("display"),
        "matchDay": base.get("gameDay") or None,
        "date": date.get("dateTimeUTC"),
        "stadium": {"id": str(stadium_id), "name": (stadium or {}).get("name")} if stadium_id else None,
        "attendance": (game.get("extendedDetails") or {}).get("crowdSize") or None,
        **{
            name: {
                **entity(side.get("clubId"), clubs),
                "score": score.get(name),
                "formation": (side.get("tactic") or {}).get("tactic"),
                "coach": entity(side.get("coachId"), coaches),
                "stats": team_stats(side.get("clubStatistics")),
                "startingLineup": [lineup_player(p) for p in lineups[name]["players"]],
                "substitutes": [lineup_player(p) for p in lineups[name]["substitutes"]],
            }
            for name, side in sides.items()
        },
        "events": [
            {
                "type": EVENT_TYPES[action["type"]],
                "minute": action.get("minute"),
                "addedTime": action.get("addedTime") or None,
                "clubId": str(action["clubId"]) if action.get("clubId") else None,
                "player": entity(action.get("activePlayerId"), players),
                "relatedPlayer": entity(action.get("passivePlayerId"), players),
                "card": card_type(action) if action["type"] == "CARD" else None,
                "score": action.get("score") if action["type"] == "GOAL" else None,
            }
            for action in sorted(actions, key=lambda a: (a.get("minute") or 0, a.get("addedTime") or 0))
        ],
    }


def card_type(action: dict) -> Optional[str]:
    """Card colour, read from the season counter upstream increments (`seasonYellowCard`, `seasonRedCard`, ...)."""
    keys = " ".join((action.get("details") or {}).keys())
    if "YellowRed" in keys:
        return "secondYellow"
    if "Red" in keys:
        return "red"
    if "Yellow" in keys:
        return "yellow"
    return None


def team_stats(statistics: Optional[dict]) -> Optional[dict]:
    """A side's match statistics, or None when upstream has none for the match."""
    if not statistics:
        return None
    return {name: (statistics.get(group) or {}).get(field) for name, (group, field) in TEAM_STATS.items()}
