from transfermarkt_api.exceptions import NotFound, UpstreamError
from transfermarkt_api.tfmkt import TfmktClient
from transfermarkt_api.tfmkt.reference import get_reference


async def list_clubs(tfmkt: TfmktClient, country_id: int) -> dict:
    """List the clubs available in the upstream country directory, preserving its order."""
    reference = await get_reference(tfmkt)
    country_name = reference.country_name(country_id)
    if country_name is None:
        raise NotFound(f"Country not found: {country_id}")

    directory = await tfmkt.country_clubs(country_id)
    if not isinstance(directory, dict) or not isinstance(directory.get("clubIds"), list):
        raise UpstreamError(f"Unexpected upstream payload for /country/{country_id}/club")
    club_ids = list(dict.fromkeys(str(club_id) for club_id in directory["clubIds"]))
    clubs = await tfmkt.clubs(club_ids)
    return {
        "countryId": country_id,
        "countryName": country_name,
        "clubs": [{"id": club_id, "name": clubs.get(club_id, {}).get("name")} for club_id in club_ids],
    }
