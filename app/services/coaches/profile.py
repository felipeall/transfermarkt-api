import asyncio

from app.tfmkt import TfmktClient
from app.tfmkt.reference import Reference, date_of_birth, full_url, get_reference, nationality_ids


def coach_summary(coach: dict, reference: Reference) -> dict:
    """Map an upstream coach record to the public coach fields."""
    birth = coach.get("birthPlaceDetails") or {}
    return {
        "id": str(coach["id"]),
        "url": full_url(coach.get("relativeUrl")),
        "name": coach.get("name"),
        "nameInHomeCountry": (coach.get("nationalityDetails") or {}).get("passportName") or None,
        "imageUrl": coach.get("portraitUrl"),
        "dateOfBirth": date_of_birth(coach),
        "age": (coach.get("lifeDates") or {}).get("age"),
        "placeOfBirth": {
            "city": birth.get("placeOfBirth") or None,
            "country": reference.country_name(birth.get("countryOfBirthId")),
        },
        "citizenship": reference.country_names(*nationality_ids(coach)),
        "license": ((coach.get("attributes") or {}).get("license") or {}).get("name"),
    }


async def get_coach_profile(tfmkt: TfmktClient, coach_id: str) -> dict:
    """Coach profile. The upstream record has no current club; use a club profile's `coach` for that."""
    coach, reference = await asyncio.gather(tfmkt.coach(coach_id), get_reference(tfmkt))
    return coach_summary(coach, reference)
