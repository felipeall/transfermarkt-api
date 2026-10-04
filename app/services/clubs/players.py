import asyncio
from typing import Optional

from app.tfmkt import TfmktClient
from app.tfmkt.reference import (
    current_assignment,
    date_of_birth,
    get_reference,
    height_cm,
    market_value_of,
    nationality_ids,
)


async def get_club_players(tfmkt: TfmktClient, club_id: str, season_id: Optional[str] = None) -> dict:
    """
    Squad of a club for a season (current squad when `season_id` is omitted).

    Player details come from today's player records. `signedFrom` (and `joinedOn` for past seasons) come from the
    latest transfer into this club up to that season. For a past season, other time-dependent fields (age, contract,
    market value) are null rather than today's values, and `currentClub` names where the player is now.
    Every squad member is returned, even if its player record is missing upstream.
    """
    squad, reference = await asyncio.gather(tfmkt.club_squad(club_id, season_id), get_reference(tfmkt))
    members = squad.get("squad") or []
    player_ids = [str(m["playerId"]) for m in members]
    is_current = all(m.get("type") == "current" for m in members)

    players, histories = await asyncio.gather(
        tfmkt.players(player_ids),
        asyncio.gather(*(tfmkt.player_transfer_history(i) for i in player_ids)),
    )
    max_season = int(season_id) if season_id and not is_current else None
    arrivals = {i: latest_arrival(history, club_id, max_season) for i, history in zip(player_ids, histories)}
    assignments = {i: current_assignment(players.get(i, {})) for i in player_ids}
    squad_members = {str(member["playerId"]): member for member in members}
    clubs = await tfmkt.clubs(
        [a["transferSource"]["clubId"] for a in arrivals.values() if a]
        + ([] if is_current else [a["clubId"] for a in assignments.values() if a]),
    )

    result = []
    for player_id in player_ids:
        player = players.get(player_id, {})
        attributes = player.get("attributes") or {}
        assignment = assignments[player_id]
        arrival = arrivals[player_id]
        entry = {
            "id": player_id,
            "name": player.get("name"),
            "imageUrl": player.get("portraitUrl"),
            "shirtNumber": squad_members[player_id].get("shirtNumber"),
            "isCaptain": squad_members[player_id].get("isCaptain"),
            "position": (attributes.get("position") or {}).get("name"),
            "dateOfBirth": date_of_birth(player),
            "nationality": reference.country_names(*nationality_ids(player)),
            "height": height_cm(player),
            "foot": (attributes.get("preferredFoot") or {}).get("name"),
            "signedFrom": clubs.get(str(arrival["transferSource"]["clubId"]), {}).get("name") if arrival else None,
        }
        if is_current:
            in_this_club = assignment is not None and str(assignment.get("clubId")) == str(club_id)
            entry |= {
                "age": (player.get("lifeDates") or {}).get("age"),
                "joinedOn": assignment.get("start") if in_this_club else None,
                "contract": attributes.get("contractUntil"),
                "marketValue": market_value_of((player.get("marketValueDetails") or {}).get("current")),
            }
        else:
            entry |= {
                "joinedOn": (arrival["details"].get("date") or "")[:10] or None if arrival else None,
                "currentClub": clubs.get(str(assignment["clubId"]), {}).get("name") if assignment else None,
            }
        result.append(entry)

    return {"id": club_id, "players": result}


def latest_arrival(history: Optional[dict], club_id: str, max_season: Optional[int]) -> Optional[dict]:
    """The most recent completed transfer into `club_id`, optionally limited to seasons up to `max_season`."""
    records = ((history or {}).get("history") or {}).get("terminated") or []
    arrivals = [
        record
        for record in records
        if str(record["transferDestination"]["clubId"]) == str(club_id)
        and (max_season is None or (record["details"].get("seasonId") or 0) <= max_season)
    ]
    return max(arrivals, key=lambda record: record["details"].get("date") or "", default=None)
