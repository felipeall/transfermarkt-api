from datetime import date
from typing import Optional

from app.tfmkt import TfmktClient
from app.tfmkt.reference import last_page_number, season_label

PAGE_SIZE = 15  # the website's injury history page size, kept for pagination compatibility


async def get_player_injuries(tfmkt: TfmktClient, player_id: str, page_number: int) -> dict:
    """
    Injury history, most recent first, paginated locally.

    `days` counts both the first and last day, as the website does (upstream `durationDetails.days` is one less).
    """
    injuries = (await tfmkt.player_injuries(player_id)).get("injuries") or []
    page = injuries[(page_number - 1) * PAGE_SIZE : page_number * PAGE_SIZE]

    return {
        "id": player_id,
        "pageNumber": page_number,
        "lastPageNumber": last_page_number(len(injuries), PAGE_SIZE),
        "injuries": [
            {
                "season": season_label(injury.get("seasonId")),
                "injury": injury.get("name"),
                "fromDate": injury.get("start"),
                "untilDate": injury.get("end"),
                "days": inclusive_days(injury),
                "gamesMissed": injury.get("missedGamesCount"),
            }
            for injury in page
        ],
    }


def inclusive_days(injury: dict) -> Optional[int]:
    """Injury length in days, counting both the first and the last day."""
    if injury.get("start") and injury.get("end"):
        return (date.fromisoformat(injury["end"]) - date.fromisoformat(injury["start"])).days + 1
    days = (injury.get("durationDetails") or {}).get("days")
    return days + 1 if days is not None else None
