import asyncio

from app.tfmkt import TfmktClient
from app.tfmkt.reference import (
    current_assignment,
    get_reference,
    last_page_number,
    market_value_of,
    nationality_ids,
)


async def search_players(tfmkt: TfmktClient, query: str, page_number: int) -> dict:
    """Search players by name. Results keep the upstream search ranking."""
    search = await tfmkt.quick_search(query, page_number)
    player_ids = [str(i) for i in search["result"]["playerIds"]]

    players, reference = await asyncio.gather(tfmkt.players(player_ids), get_reference(tfmkt))
    assignments = {i: current_assignment(players.get(i, {})) for i in player_ids}
    clubs = await tfmkt.clubs(a["clubId"] for a in assignments.values() if a)

    results = []
    for player_id in player_ids:
        player = players.get(player_id, {})
        attributes = player.get("attributes") or {}
        assignment = assignments[player_id]
        club_id = str(assignment["clubId"]) if assignment else None
        results.append(
            {
                "id": player_id,
                "name": player.get("name"),
                "position": (attributes.get("position") or {}).get("shortName"),
                "club": {"id": club_id, "name": clubs.get(club_id, {}).get("name")} if club_id else None,
                "age": (player.get("lifeDates") or {}).get("age"),
                "nationalities": reference.country_names(*nationality_ids(player)),
                "marketValue": market_value_of((player.get("marketValueDetails") or {}).get("current")),
            },
        )

    return {
        "query": query,
        "pageNumber": page_number,
        "lastPageNumber": last_page_number(search["totalCount"]["players"]),
        "results": results,
    }
