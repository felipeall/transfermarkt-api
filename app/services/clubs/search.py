import asyncio

from app.tfmkt import TfmktClient
from app.tfmkt.reference import get_reference, last_page_number, market_value_of


async def search_clubs(tfmkt: TfmktClient, query: str, page_number: int) -> dict:
    """Search clubs by name. Results keep the upstream search ranking."""
    search = await tfmkt.quick_search(query, page_number)
    club_ids = [str(i) for i in search["result"]["clubIds"]]

    clubs, reference = await asyncio.gather(tfmkt.clubs(club_ids), get_reference(tfmkt))

    results = []
    for club_id in club_ids:
        club = clubs.get(club_id, {})
        squad = club.get("squadDetails") or {}
        results.append(
            {
                "id": club_id,
                "url": club.get("relativeUrl"),
                "name": club.get("name"),
                "country": reference.country_name((club.get("baseDetails") or {}).get("countryId")),
                "squad": squad.get("squadSize"),
                "marketValue": market_value_of(squad.get("currentMarketValue")),
            },
        )

    return {
        "query": query,
        "pageNumber": page_number,
        "lastPageNumber": last_page_number(search["totalCount"]["clubs"]),
        "results": results,
    }
