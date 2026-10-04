"""Lookups into tfmkt reference data (`/attributes`) and small helpers shared by JSON-backed services."""

import math
from typing import Optional, Union

from app.tfmkt.client import TfmktClient

TRANSFERMARKT_URL = "https://www.transfermarkt.com"
RETIRED_CLUB_ID = "123"
SEARCH_PAGE_SIZE = 10  # quick-search returns 10 IDs per category per page


class Reference:
    """Indexed view of `/attributes`."""

    def __init__(self, attributes: dict) -> None:
        """Index the `/attributes` lists by ID."""
        self.countries = {c["id"]: c for c in attributes.get("countries", [])}
        self.confederations = {c["id"]: c for c in attributes.get("confederations", [])}
        self.competition_types = {c["id"]: c for c in attributes.get("competitionTypes", [])}
        self.contracts = {c["id"]: c for c in attributes.get("contracts", [])}
        self.positions = {p["id"]: p for p in attributes.get("positions", [])}

    def country(self, country_id: Optional[Union[int, str]]) -> dict:
        """Record of a country, or an empty dict if unknown."""
        return self.countries.get(_int(country_id)) or {}

    def country_name(self, country_id: Optional[Union[int, str]]) -> Optional[str]:
        """Name of a country, or None if unknown."""
        return self.country(country_id).get("name")

    def country_names(self, *country_ids: Optional[Union[int, str]]) -> list[str]:
        """Names of the known countries among the given IDs, in order."""
        return [name for name in (self.country_name(i) for i in country_ids) if name]

    def confederation_name(self, confederation_id: Optional[Union[int, str]]) -> Optional[str]:
        """Short name of a confederation (e.g. UEFA), or None if unknown."""
        return self.confederations.get(_int(confederation_id), {}).get("name")

    def competition_type_name(self, type_id: Optional[Union[int, str]]) -> Optional[str]:
        """Name of a competition type (e.g. First Tier), or None if unknown."""
        return self.competition_types.get(_int(type_id), {}).get("name")

    def position_name(self, position_id: Optional[Union[int, str]]) -> Optional[str]:
        """Name of a position (e.g. Right Winger), or None if unknown."""
        return self.positions.get(_int(position_id), {}).get("name")

    def contract_option_name(self, option_id: Optional[Union[int, str]]) -> Optional[str]:
        """Name of a contract option, or None if unknown."""
        return self.contracts.get(_int(option_id), {}).get("name")


async def get_reference(tfmkt: TfmktClient) -> Reference:
    """Fetch `/attributes` (cached) and index it."""
    return Reference(await tfmkt.attributes())


def _int(value: object) -> Optional[int]:
    """Convert to int, or None when the value is not a number."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def value_of(money: Optional[dict]) -> Optional[int]:
    """Numeric value of a tfmkt money object (`{"value": 15000000, "currency": "EUR", ...}`)."""
    if not money or money.get("value") is None:
        return None
    return int(money["value"])


def market_value_of(money: Optional[dict]) -> Optional[int]:
    """Like `value_of`, but 0 means "no valuation" (the website shows "-"), so it becomes None."""
    return value_of(money) or None


def full_url(relative_url: Optional[str]) -> Optional[str]:
    """Absolute website URL for a relative upstream URL."""
    return f"{TRANSFERMARKT_URL}{relative_url}" if relative_url else None


def season_label(season_id: Optional[Union[int, str]]) -> Optional[str]:
    """Split-year season label used by the website, e.g. 2025 -> "25/26"."""
    year = _int(season_id)
    if year is None:
        return None
    return f"{year % 100:02d}/{(year + 1) % 100:02d}"


def last_page_number(total: Optional[int], page_size: int = SEARCH_PAGE_SIZE) -> int:
    """Number of pages needed for `total` results (at least 1)."""
    return max(1, math.ceil((total or 0) / page_size))


def current_assignment(player: dict) -> Optional[dict]:
    """The player's current club assignment. Selected by type: national-team assignments can come first."""
    return next((a for a in player.get("clubAssignments") or [] if a.get("type") == "current"), None)


def date_of_birth(player: dict) -> Optional[str]:
    """ISO date of birth, or None when upstream marks it unknown."""
    life = player.get("lifeDates") or {}
    return None if life.get("isDateOfBirthUnknown") else life.get("dateOfBirth")


def height_cm(player: dict) -> Optional[int]:
    """Height in centimetres (upstream gives metres)."""
    height = (player.get("attributes") or {}).get("height")
    return round(height * 100) if height else None


def nationality_ids(player: dict) -> tuple:
    """First and second nationality country IDs."""
    nationalities = (player.get("nationalityDetails") or {}).get("nationalities") or {}
    return nationalities.get("nationalityId"), nationalities.get("secondNationalityId")
