"""
Correct values for bugs reproduced against recorded pages (October 2026).

Each test asserts what the API *should* return. They are strict xfails: once a fix lands the test
passes, pytest reports XPASS as a failure, and the marker must be removed.
"""

import pytest
from fastapi.testclient import TestClient


def known_bug(reason: str) -> pytest.MarkDecorator:
    """Mark a test as a strict xfail for a reproduced bug."""
    return pytest.mark.xfail(strict=True, reason=reason)


@known_bug("#111: date of birth now rendered as dd/mm/yyyy; REGEX_DOB_AGE expects 'Jun 24, 1987'")
def test_player_profile_date_of_birth_and_age(client: TestClient) -> None:
    """Profile has the date of birth and age."""
    body = client.get("/players/28003/profile").json()

    assert body.get("dateOfBirth") == "1987-06-24"
    assert body.get("age") == 39


@known_bug("#111: dd/mm/yyyy parsed month-first by dateutil")
def test_player_retired_since_is_day_first(client: TestClient) -> None:
    """Retirement date is parsed day-first."""
    body = client.get("/players/5023/profile").json()

    assert body["retiredSince"] == "2023-08-02"


@known_bug("#111: dd/mm/yyyy parsed month-first by dateutil")
def test_market_value_history_is_chronological(client: TestClient) -> None:
    """Market value history is in date order."""
    history = client.get("/players/28003/market_value").json()["marketValueHistory"]
    dates = [entry["date"] for entry in history]

    assert dates == sorted(dates)


@known_bug("#111: dd/mm/yyyy parsed month-first by dateutil")
def test_transfer_date_is_day_first(client: TestClient) -> None:
    """Transfer dates are parsed day-first."""
    transfers = client.get("/players/28003/transfers").json()["transfers"]
    to_psg = next(t for t in transfers if t["clubTo"]["id"] == "583")

    assert to_psg["date"] == "2021-08-10"


@known_bug("#111: dd/mm/yyyy parsed month-first by dateutil")
def test_club_players_joined_on_is_day_first(client: TestClient) -> None:
    """Squad joined dates are parsed day-first."""
    players = client.get("/clubs/131/players").json()["players"]
    joan_garcia = next(p for p in players if p["id"] == "561613")

    assert joan_garcia["joinedOn"] == "2025-07-01"


def test_player_stats_not_empty(client: TestClient) -> None:
    """Stats are returned for a player with a long career."""
    body = client.get("/players/28003/stats").json()

    assert body["stats"]


@known_bug("#107: stadiumName/stadiumSeats required but absent upstream")
def test_club_profile_without_stadium(client: TestClient) -> None:
    """A club without stadium data still has a profile (#107)."""
    assert client.get("/clubs/3331/profile").status_code == 200


@known_bug("#106: currentTransferRecord/stadium required but absent for national teams")
def test_national_team_club_profile(client: TestClient) -> None:
    """A national team has a club profile (#106)."""
    assert client.get("/clubs/3383/profile").status_code == 200
