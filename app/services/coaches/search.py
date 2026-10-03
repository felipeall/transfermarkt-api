import asyncio

from app.services.coaches.profile import coach_summary
from app.tfmkt import TfmktClient
from app.tfmkt.reference import get_reference, last_page_number


async def search_coaches(tfmkt: TfmktClient, query: str, page_number: int) -> dict:
    """Search coaches by name. Results keep the upstream search ranking."""
    search = await tfmkt.quick_search(query, page_number)
    coach_ids = [str(i) for i in search["result"]["coachIds"]]
    coaches, reference = await asyncio.gather(tfmkt.coaches(coach_ids), get_reference(tfmkt))

    return {
        "query": query,
        "pageNumber": page_number,
        "lastPageNumber": last_page_number(search["totalCount"]["coaches"]),
        "results": [coach_summary(coaches.get(i, {"id": i}), reference) for i in coach_ids],
    }
