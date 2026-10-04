import asyncio
from datetime import date
from typing import Optional

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
    national = next((a for a in player.get("clubAssignments") or [] if a.get("type") == "nationalTeam"), None)
    national_id = str(national["clubId"]) if national and national.get("clubId") else None

    clubs = await tfmkt.clubs(i for i in (club_id, last_club_id, national_id) if i)
    agency = attributes.get("consultantAgency") or {}
    life = player.get("lifeDates") or {}
    values = player.get("marketValueDetails") or {}
    trend = ((values.get("delta") or {}).get("type") or "").lower()

    return {
        "id": player_id,
        "url": full_url(player.get("relativeUrl")),
        "name": player.get("name"),
        "fullName": player.get("displayName") or None,
        "nameInHomeCountry": (player.get("nationalityDetails") or {}).get("passportName") or None,
        "imageUrl": player.get("portraitUrl"),
        "dateOfBirth": date_of_birth(player),
        "dateOfDeath": None if life.get("isDateOfDeathUnknown") else life.get("dateOfDeath"),
        "placeOfBirth": {
            "city": birth.get("placeOfBirth") or None,
            "country": reference.country_name(birth.get("countryOfBirthId")),
        },
        "age": life.get("age"),
        "height": height_cm(player),
        "citizenship": reference.country_names(*nationality_ids(player)),
        "isRetired": is_retired,
        "retiredSince": assignment.get("start") if is_retired else None,
        "position": {
            "main": (attributes.get("position") or {}).get("name"),
            "group": attributes.get("positionGroupName"),
            "other": [
                position["name"]
                for position in (attributes.get("firstSidePosition"), attributes.get("secondSidePosition"))
                if position
            ],
        },
        "foot": (attributes.get("preferredFoot") or {}).get("name"),
        "shirtNumber": shirt_number_label(assignment.get("shirtNumber")),
        "club": {
            "id": club_id,
            "name": clubs.get(club_id, {}).get("name"),
            "joined": assignment.get("start"),
            "isCaptain": assignment.get("isCaptain"),
            "contractExpires": attributes.get("contractUntil"),
            "lastContractRenewal": date_from_parts(attributes.get("lastContractRenewal")),
            "contractOption": reference.contract_option_name(attributes.get("contractOptionId")),
            "lastClubId": last_club_id,
            "lastClubName": clubs.get(last_club_id, {}).get("name"),
        },
        "nationalTeam": {
            "id": national_id,
            "name": clubs.get(national_id, {}).get("name"),
            "shirtNumber": shirt_number_label(national.get("shirtNumber")),
            "isCaptain": national.get("isCaptain"),
            "debut": national.get("debut"),
        }
        if national_id
        else None,
        "marketValue": market_value_of(values.get("current")),
        "marketValueDetails": {
            "lastUpdated": (values.get("current") or {}).get("determined"),
            "trend": trend if trend in ("increased", "decreased", "unchanged") else None,
            "previous": dated_value(values.get("previous")),
            "highest": dated_value(values.get("highest")),
        }
        if values
        else None,
        "agent": {"name": agency.get("name"), "url": agency.get("relativeUrl")} if agency else None,
        "outfitter": (attributes.get("outfitter") or {}).get("name"),
    }


def shirt_number_label(number: Optional[int]) -> Optional[str]:
    """Shirt number as the website shows it, e.g. "#10"."""
    return f"#{number}" if number is not None else None


def dated_value(money: Optional[dict]) -> Optional[dict]:
    """`{value, date}` for a market value with the date it was set, or None when there is no valuation."""
    value = market_value_of(money)
    return {"value": value, "date": money.get("determined")} if value else None


def date_from_parts(parts: Optional[dict]) -> Optional[str]:
    """ISO date from upstream `{year, month, day}`, or None when incomplete or invalid."""
    try:
        return date(parts["year"], parts["month"], parts["day"]).isoformat()
    except (TypeError, KeyError, ValueError):
        return None
