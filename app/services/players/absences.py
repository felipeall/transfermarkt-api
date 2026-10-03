from app.services.players.injuries import PAGE_SIZE, inclusive_days
from app.tfmkt import TfmktClient
from app.tfmkt.reference import last_page_number, season_label


async def get_player_absences(tfmkt: TfmktClient, player_id: str, page_number: int) -> dict:
    """
    Non-injury absences (suspensions, national-team call-ups, leave), most recent first, paginated like injuries.

    `days` counts both the first and last day, as for injuries.
    """
    absences = (await tfmkt.player_absences(player_id)).get("absences") or []
    page = absences[(page_number - 1) * PAGE_SIZE : page_number * PAGE_SIZE]
    competitions = await tfmkt.competitions(a.get("competitionId") for a in page if a.get("competitionId"))

    return {
        "id": player_id,
        "pageNumber": page_number,
        "lastPageNumber": last_page_number(len(absences), PAGE_SIZE),
        "absences": [
            {
                "season": season_label(absence.get("seasonId")),
                "reason": absence.get("name"),
                "competitionId": absence.get("competitionId") or None,
                "competitionName": competitions.get(absence.get("competitionId") or "", {}).get("name"),
                "fromDate": absence.get("start"),
                "untilDate": absence.get("end"),
                "days": inclusive_days(absence),
                "gamesMissed": absence.get("missedGamesCount"),
            }
            for absence in page
        ],
    }
