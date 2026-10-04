import asyncio

from app.tfmkt import TfmktClient
from app.tfmkt.reference import get_reference, market_value_of, value_of


async def get_club_profile(tfmkt: TfmktClient, club_id: str) -> dict:
    """
    Club profile.

    `officialName`, the address and the colors come from the club's superior (parent) club record. For national
    teams that record is the football association, so `officialName` is omitted for them.
    """
    club, squad, stadium, club_coach, reference = await asyncio.gather(
        tfmkt.club(club_id),
        tfmkt.club_squad(club_id),
        tfmkt.club_stadium(club_id),
        tfmkt.club_coach(club_id),
        get_reference(tfmkt),
    )
    coach_id = str(club_coach["coachId"]) if club_coach and club_coach.get("coachId") else None
    coaches = await tfmkt.coaches([coach_id]) if coach_id else {}
    base = club.get("baseDetails") or {}
    superior = base.get("superiorClub") or {}
    location = superior.get("location") or {}
    squad_details = club.get("squadDetails") or {}
    competition_id = base.get("primaryCompetitionId") or None
    competition = (await tfmkt.competitions([competition_id])).get(competition_id, {}) if competition_id else {}
    competition_origin = competition.get("originDetails") or {}
    country = reference.country(base.get("countryId"))
    stadium_location = (stadium or {}).get("location") or {}
    building = (stadium or {}).get("buildingDetails") or {}
    postcode_city = " ".join(part for part in (location.get("postcode"), location.get("city")) if part)

    return {
        "id": club_id,
        "url": club.get("relativeUrl"),
        "name": club.get("name"),
        "shortName": base.get("shortName") or None,
        "abbreviation": base.get("abbreviation") or None,
        "clubCode": (club.get("preferences") or {}).get("clubCode") or None,
        "officialName": None if base.get("isNationalTeam") else superior.get("name") or None,
        "image": club.get("crestUrl"),
        "addressLine1": (location.get("street") or "").strip() or None,
        "addressLine2": postcode_city or None,
        "addressLine3": reference.country_name(location.get("countryId")),
        "colors": [color for color in (superior.get("colors") or {}).values() if color],
        "stadiumName": (stadium or {}).get("name"),
        "stadiumSeats": (stadium or {}).get("capacity"),
        "stadium": {
            "id": str(stadium["id"]) if stadium.get("id") is not None else None,
            "name": stadium.get("name") or None,
            "capacity": stadium.get("capacity"),
            "internationalCapacity": stadium.get("internationalCapacity"),
            "website": stadium.get("url") or None,
            "addressLine1": (stadium_location.get("street") or "").strip() or None,
            "addressLine2": " ".join(
                part for part in (stadium_location.get("postcode"), stadium_location.get("city")) if part
            )
            or None,
            "countryId": str(stadium_location["countryId"]) if stadium_location.get("countryId") is not None else None,
            "countryName": reference.country_name(stadium_location.get("countryId")),
            "latitude": stadium_location.get("latitude"),
            "longitude": stadium_location.get("longitude"),
            "buildYear": building.get("buildYear") or None,
            "renovationYear": building.get("renovationYear") or None,
            "fieldLength": building.get("fieldLength") or None,
            "fieldWidth": building.get("fieldWidth") or None,
            "fieldSurface": building.get("fieldSurface") or None,
            "images": list(dict.fromkeys(image["url"] for image in stadium.get("images") or [] if image.get("url"))),
        }
        if stadium
        else None,
        "currentMarketValue": market_value_of(squad_details.get("currentMarketValue")),
        "confederation": (
            reference.confederation_name(country.get("confederationId")) if base.get("isNationalTeam") else None
        ),
        "coach": {
            "id": coach_id,
            "name": coaches.get(coach_id, {}).get("name"),
            "since": (club_coach.get("startDate") or "")[:10] or None,
        }
        if coach_id
        else None,
        "squad": {
            "size": squad_details.get("squadSize"),
            "averageAge": float(squad_details["averageAgeDisplay"]) if squad_details.get("averageAgeDisplay") else None,
            "foreigners": squad.get("foreignCount"),
            "nationalTeamPlayers": squad.get("nationalCount"),
            "domesticPlayers": squad.get("localCount"),
            "averageMarketValue": market_value_of(squad_details.get("averageMarketValue")),
            "acquisitionValue": value_of(squad_details.get("acquisitionValue")),
            "top18PlayersMarketValue": market_value_of(squad_details.get("top18PlayersMarketValue")),
            "top18SharePercentage": (squad_details.get("top18SharePercentage") or {}).get("value"),
        },
        "league": {
            "id": competition_id,
            "name": competition.get("name"),
            "countryId": str(competition_origin["countryId"]) if competition_origin.get("countryId") else None,
            "countryName": reference.country_name(competition_origin.get("countryId")),
            "tier": reference.competition_type_name(competition.get("typeId")),
        },
        "historicalNames": [
            {
                "name": entry.get("name") or None,
                "shortName": entry.get("shortName") or None,
                "abbreviation": entry.get("abbreviation") or None,
                "seasonId": str(entry["seasonId"]) if entry.get("seasonId") is not None else None,
            }
            for entry in (club.get("historical") or {}).get("names") or []
        ],
        "historicalCrests": list(
            dict.fromkeys(image["url"] for image in (club.get("historical") or {}).get("images") or [])
        ),
    }
