import asyncio
from typing import Optional

from app.tfmkt import TfmktClient
from app.tfmkt.reference import get_reference, last_page_number, value_of


async def search_competitions(tfmkt: TfmktClient, query: str, page_number: int) -> dict:
    """
    Search competitions by name.

    `clubs` and `players` count the current season's member clubs and the sum of their squad sizes, and
    `meanMarketValue` is the total market value divided by the number of clubs. This reproduces the website's
    figures (e.g. Premier League 2026: 20 clubs, 542 players).
    """
    search = await tfmkt.quick_search(query, page_number)
    competition_ids = [str(i) for i in search["result"]["competitionIds"]]

    competitions, reference, memberships = await asyncio.gather(
        tfmkt.competitions(competition_ids),
        get_reference(tfmkt),
        # some competitions (e.g. finished tournaments) may have no current membership
        asyncio.gather(*(tfmkt.get_optional(f"/competition/{i}/club") for i in competition_ids)),
    )
    club_ids_by_competition = {
        i: [str(c) for c in m["clubIds"]] if m else None for i, m in zip(competition_ids, memberships)
    }
    clubs = await tfmkt.clubs(c for ids in club_ids_by_competition.values() for c in ids or [])

    results = []
    for competition_id in competition_ids:
        competition = competitions.get(competition_id, {})
        club_ids = club_ids_by_competition[competition_id]
        total_market_value = value_of(competition.get("totalMarketValue"))
        origin = competition.get("originDetails") or {}
        results.append(
            {
                "id": competition_id,
                "name": competition.get("name"),
                "country": reference.country_name(origin.get("countryId")),
                "clubs": len(club_ids) if club_ids is not None else None,
                "players": squad_total(clubs, club_ids),
                "totalMarketValue": total_market_value,
                "meanMarketValue": total_market_value // len(club_ids) if total_market_value and club_ids else None,
                "continent": reference.confederation_name(origin.get("confederationId")),
            },
        )

    return {
        "query": query,
        "pageNumber": page_number,
        "lastPageNumber": last_page_number(search["totalCount"]["competitions"]),
        "results": results,
    }


def squad_total(clubs: dict, club_ids: Optional[list[str]]) -> Optional[int]:
    """Sum the squad sizes of the given clubs; None when the membership is unknown."""
    if club_ids is None:
        return None
    return sum((clubs.get(c, {}).get("squadDetails") or {}).get("squadSize") or 0 for c in club_ids)
