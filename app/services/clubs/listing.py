from fastapi import HTTPException

from app.tfmkt import TfmktClient
from app.tfmkt.reference import get_reference


async def list_clubs(tfmkt: TfmktClient, country_id: int) -> dict:
    """List the clubs available in the upstream country directory, preserving its order."""
    reference = await get_reference(tfmkt)
    country_name = reference.country_name(country_id)
    if country_name is None:
        raise HTTPException(status_code=404, detail=f"Country not found: {country_id}")

    directory = await tfmkt.country_clubs(country_id)
    club_ids = list(dict.fromkeys(str(club_id) for club_id in directory.get("clubIds") or []))
    clubs = await tfmkt.clubs(club_ids)
    return {
        "countryId": country_id,
        "countryName": country_name,
        "clubs": [{"id": club_id, "name": clubs.get(club_id, {}).get("name")} for club_id in club_ids],
    }
