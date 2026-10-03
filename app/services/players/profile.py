import asyncio

from app.tfmkt import TfmktClient
from app.tfmkt.reference import (
    RETIRED_CLUB_ID,
    current_assignment,
    date_of_birth,
    full_url,
    get_reference,
    height_cm,
    market_value_of,
    nationality_ids,
)


async def get_player_profile(tfmkt: TfmktClient, player_id: str) -> dict:
    """
    Player profile.

    A player is retired when assigned to Transfermarkt's special "Retired" club (ID 123); `retiredSince` is the start
    of that assignment and `club.lastClubId` names the club before it.
    """
    player, reference = await asyncio.gather(tfmkt.player(player_id), get_reference(tfmkt))
    attributes = player.get("attributes") or {}
    birth = player.get("birthPlaceDetails") or {}
    assignment = current_assignment(player) or {}
    club_id = str(assignment["clubId"]) if assignment.get("clubId") else None
    is_retired = club_id == RETIRED_CLUB_ID
    last_club_id = str(player["lastClubId"]) if player.get("lastClubId") else None

    clubs = await tfmkt.clubs(i for i in (club_id, last_club_id) if i)
    agency = attributes.get("consultantAgency") or {}
    shirt_number = assignment.get("shirtNumber")

    return {
        "id": player_id,
        "url": full_url(player.get("relativeUrl")),
        "name": player.get("name"),
        "fullName": player.get("displayName") or None,
        "nameInHomeCountry": (player.get("nationalityDetails") or {}).get("passportName") or None,
        "imageUrl": player.get("portraitUrl"),
        "dateOfBirth": date_of_birth(player),
        "placeOfBirth": {
            "city": birth.get("placeOfBirth") or None,
            "country": reference.country_name(birth.get("countryOfBirthId")),
        },
        "age": (player.get("lifeDates") or {}).get("age"),
        "height": height_cm(player),
        "citizenship": reference.country_names(*nationality_ids(player)),
        "isRetired": is_retired,
        "retiredSince": assignment.get("start") if is_retired else None,
        "position": {
            "main": (attributes.get("position") or {}).get("name"),
            "other": [
                position["name"]
                for position in (attributes.get("firstSidePosition"), attributes.get("secondSidePosition"))
                if position
            ],
        },
        "foot": (attributes.get("preferredFoot") or {}).get("name"),
        "shirtNumber": f"#{shirt_number}" if shirt_number is not None else None,
        "club": {
            "id": club_id,
            "name": clubs.get(club_id, {}).get("name"),
            "joined": assignment.get("start"),
            "contractExpires": attributes.get("contractUntil"),
            "contractOption": reference.contract_option_name(attributes.get("contractOptionId")),
            "lastClubId": last_club_id,
            "lastClubName": clubs.get(last_club_id, {}).get("name"),
        },
        "marketValue": market_value_of((player.get("marketValueDetails") or {}).get("current")),
        "agent": {"name": agency.get("name"), "url": agency.get("relativeUrl")} if agency else None,
        "outfitter": (attributes.get("outfitter") or {}).get("name"),
    }
