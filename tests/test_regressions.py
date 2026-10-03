"""
Regression tests for bugs reproduced against the v3 HTML scraper (October 2026), fixed by the JSON migration.

- #111: dd/mm/yyyy dates parsed month-first; date of birth regex no longer matched.
- Stats page became client-rendered, so stats were always empty.
- #106, #107: club profiles failed when stadium/transfer record were absent.
"""

from fastapi.testclient import TestClient


def test_player_profile_date_of_birth_and_age(client: TestClient) -> None:
    """Profile has the date of birth and age."""
    body = client.get("/players/28003/profile").json()

    assert body.get("dateOfBirth") == "1987-06-24"
    assert body.get("age") == 39


def test_player_retired_since_is_day_first(client: TestClient) -> None:
    """Retirement date is parsed day-first."""
    body = client.get("/players/5023/profile").json()

    assert body["retiredSince"] == "2023-08-02"


def test_market_value_history_is_chronological(client: TestClient) -> None:
    """Market value history is in date order."""
    history = client.get("/players/28003/market_value").json()["marketValueHistory"]
    dates = [entry["date"] for entry in history]

    assert dates == sorted(dates)


def test_transfer_date_is_day_first(client: TestClient) -> None:
    """Transfer dates are parsed day-first."""
    transfers = client.get("/players/28003/transfers").json()["transfers"]
    to_psg = next(t for t in transfers if t["clubTo"]["id"] == "583")

    assert to_psg["date"] == "2021-08-10"


def test_club_players_joined_on_is_day_first(client: TestClient) -> None:
    """Squad joined dates are parsed day-first."""
    players = client.get("/clubs/131/players").json()["players"]
    joan_garcia = next(p for p in players if p["id"] == "561613")

    assert joan_garcia["joinedOn"] == "2025-07-01"


def test_player_stats_not_empty(client: TestClient) -> None:
    """Stats are returned for a player with a long career."""
    body = client.get("/players/28003/stats").json()

    assert body["stats"]


def test_club_profile_without_stadium(client: TestClient) -> None:
    """A club without stadium data still has a profile (#107)."""
    assert client.get("/clubs/3331/profile").status_code == 200


def test_national_team_club_profile(client: TestClient) -> None:
    """A national team has a club profile (#106)."""
    assert client.get("/clubs/3383/profile").status_code == 200
