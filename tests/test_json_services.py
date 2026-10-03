"""Behavior of the JSON-backed endpoints: recorded upstream data plus synthetic edge cases."""

import json
from collections.abc import Iterator
from datetime import datetime

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.tfmkt import TfmktClient, get_tfmkt
from tests.snapshots import BASELINE_V3_DIR


def ok(data: object) -> httpx.Response:
    """A successful tfmkt response wrapping `data`."""
    return httpx.Response(200, json={"success": True, "message": "OK", "data": data})


@pytest.fixture
def synthetic_client() -> Iterator[tuple[TestClient, dict]]:
    """Client whose tfmkt answers come from a `routes` dict {path: data} filled by each test."""
    routes: dict = {"/attributes": {"countries": [{"id": 9, "name": "Argentina"}]}}

    def handler(request: httpx.Request) -> httpx.Response:
        """Answer from `routes`: batch routes filter by ID, unknown paths are 404."""
        path = request.url.path
        if path in ("/players", "/clubs", "/competitions"):
            ids = request.url.params.get_list("ids[]")
            return ok([entity for entity in routes.get(path, []) if entity["id"] in ids])
        if path not in routes:
            return httpx.Response(404, json={"success": False, "message": "not found"})
        return ok(routes[path])

    tfmkt = TfmktClient(base_url="https://tfmkt.test", transport=httpx.MockTransport(handler))
    app.dependency_overrides[get_tfmkt] = lambda: tfmkt
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, routes
    app.dependency_overrides.clear()


def test_jersey_numbers_without_json_source_return_501(client: TestClient) -> None:
    """Jersey numbers have no JSON source and answer 501."""
    assert client.get("/players/28003/jersey_numbers").status_code == 501


def test_unknown_player_is_404(client: TestClient) -> None:
    """Unknown player IDs answer 404."""
    assert client.get("/players/0/profile").status_code == 404


def test_retired_player(client: TestClient) -> None:
    """Retirement comes from the special Retired club; no valuation is null."""
    body = client.get("/players/5023/profile").json()

    assert body["isRetired"] is True
    assert body["club"]["id"] == "123"
    assert body["club"]["lastClubId"] == "130"
    assert body["marketValue"] is None  # upstream 0 means "no valuation"


def test_player_name_variants(client: TestClient) -> None:
    """Full name and name in home country map to displayName and passportName."""
    assert client.get("/players/8198/profile").json()["fullName"] == "Cristiano Ronaldo dos Santos Aveiro"
    assert client.get("/players/28003/profile").json()["nameInHomeCountry"] == "Lionel Andrés Messi Cuccitini"


def test_youth_clubs_split_on_closing_parenthesis(client: TestClient) -> None:
    """Youth clubs are split after each closing parenthesis."""
    youth_clubs = client.get("/players/28003/transfers").json()["youthClubs"]

    assert youth_clubs == ["Grandoli FC (1992-1995)", "Newell's Old Boys (1995-2000)"]


def test_injury_days_count_first_and_last_day(client: TestClient) -> None:
    """Injury days count both the first and the last day."""
    injury = client.get("/players/28003/injuries").json()["injuries"][0]

    assert (injury["fromDate"], injury["untilDate"], injury["days"]) == ("2026-05-26", "2026-06-06", 12)


def test_competition_search_counts_match_website(client: TestClient) -> None:
    """Competition clubs, players and mean value match the website."""
    premier_league = client.get("/competitions/search/premier%20league").json()["results"][0]

    assert (premier_league["id"], premier_league["clubs"], premier_league["players"]) == ("GB1", 20, 542)
    assert premier_league["meanMarketValue"] == premier_league["totalMarketValue"] // 20


def test_squad_keeps_members_missing_from_player_batch(synthetic_client: tuple[TestClient, dict]) -> None:
    """Squad members missing from the player batch are kept."""
    client, routes = synthetic_client
    routes["/club/1/squad"] = {
        "clubId": "1",
        "squad": [{"playerId": "10", "type": "current"}, {"playerId": "11", "type": "current"}],
        "foreignCount": 0,
        "nationalCount": 0,
    }
    routes["/players"] = [{"id": "10", "name": "Known Player"}]

    players = client.get("/clubs/1/players").json()["players"]

    assert [(p["id"], p["name"]) for p in players] == [("10", "Known Player"), ("11", None)]


def test_search_keeps_upstream_ranking(synthetic_client: tuple[TestClient, dict]) -> None:
    """Search results keep the upstream ranking and page count."""
    client, routes = synthetic_client
    routes["/quick-search"] = {"result": {"playerIds": ["2", "1"]}, "totalCount": {"players": 11}}
    routes["/players"] = [{"id": "1", "name": "One"}, {"id": "2", "name": "Two"}]

    body = client.get("/players/search/x").json()

    assert [r["id"] for r in body["results"]] == ["2", "1"]
    assert body["lastPageNumber"] == 2


def test_unknown_transfer_fee_stays_null(synthetic_client: tuple[TestClient, dict]) -> None:
    """Unknown transfer fees stay null and dates drop the time."""
    client, routes = synthetic_client
    routes["/player/7"] = {"id": "7", "attributes": {}}
    routes["/transfer/history/player/7"] = {
        "history": {
            "pending": [],
            "terminated": [
                {
                    "id": "1",
                    "transferSource": {"clubId": "2"},
                    "transferDestination": {"clubId": "3"},
                    "details": {
                        "date": "2020-07-01T00:00:00+02:00",
                        "fee": {"value": None, "compact": {"content": "-"}},
                    },
                },
            ],
        },
    }

    transfer = client.get("/players/7/transfers").json()["transfers"][0]

    assert transfer["fee"] is None
    assert transfer["date"] == "2020-07-01"


def test_player_without_transfer_history(synthetic_client: tuple[TestClient, dict]) -> None:
    """A player without transfer history has no transfers."""
    client, routes = synthetic_client
    routes["/player/7"] = {"id": "7", "attributes": {}}

    body = client.get("/players/7/transfers").json()

    assert body["transfers"] == []


def test_updated_at_reports_when_cached_data_was_fetched(client: TestClient) -> None:
    """updatedAt reports when cached data was fetched."""
    client.get("/players/28003/profile")
    tfmkt = app.dependency_overrides[get_tfmkt]()
    fetched_at = datetime(2026, 1, 2, 3, 4, 5)
    for key, (_, data) in list(tfmkt.cache.items()):
        tfmkt.cache[key] = (fetched_at, data)

    body = client.get("/players/28003/profile").json()

    assert body["updatedAt"] == fetched_at.isoformat()


def test_health_does_not_call_upstream(synthetic_client: tuple[TestClient, dict]) -> None:
    """Health answers ok without calling upstream."""
    client, routes = synthetic_client
    routes.clear()

    assert client.get("/health").json() == {"status": "ok"}


def test_player_achievements_keep_v3_titles_and_counts(client: TestClient) -> None:
    """Every v3 achievement title is present with the same count."""
    v3 = json.loads((BASELINE_V3_DIR / "players_28003_achievements.json").read_text())["body"]["achievements"]
    achievements = {a["title"].lower(): a for a in client.get("/players/28003/achievements").json()["achievements"]}

    assert {a["title"].lower(): a["count"] for a in v3}.items() <= {
        k: a["count"] for k, a in achievements.items()
    }.items()
    assert achievements["spanish champion"]["details"][0] == {
        "season": {"id": "2018", "name": "18/19"},
        "club": {"id": "131", "name": "FC Barcelona"},
        "competition": {"id": "ES1", "name": "LaLiga"},
    }


def test_market_value_worldwide_ranking(client: TestClient) -> None:
    """Market value includes the worldwide ranking."""
    assert client.get("/players/28003/market_value").json()["ranking"] == {"Worldwide": 844}


def test_historical_league_table(client: TestClient) -> None:
    """A past season's table is returned for that season."""
    body = client.get("/competitions/GB1/table?season_id=2014").json()
    champion = body["tables"][0]["rows"][0]

    assert body["seasonId"] == "2014"
    assert (champion["clubName"], champion["points"], champion["matches"]) == ("Chelsea FC", 87, 38)


def test_group_stage_tables(client: TestClient) -> None:
    """Group stages return one table per group."""
    tables = client.get("/competitions/CL/table?season_id=2020").json()["tables"]

    assert [t["name"] for t in tables][:2] == ["Group A", "Group B"]
    assert all(len(t["rows"]) == 4 for t in tables)


def test_national_career(client: TestClient) -> None:
    """National career lists the current national team first."""
    argentina = client.get("/players/28003/national_career").json()["nationalTeams"][0]

    assert (argentina["name"], argentina["status"], argentina["isCaptain"]) == ("Argentina", "current", True)


def test_club_profile_includes_current_coach(client: TestClient) -> None:
    """Club profile includes the current head coach."""
    assert client.get("/clubs/131/profile").json()["coach"] == {
        "id": "67",
        "name": "Hansi Flick",
        "since": "2024-07-01",
    }


@pytest.mark.parametrize("path", ["/players/0/achievements", "/clubs/0/achievements", "/coaches/0/profile"])
def test_unknown_ids_are_404(client: TestClient, path: str) -> None:
    """Unknown IDs answer 404 on routes that return empty data upstream."""
    assert client.get(path).status_code == 404


def test_country_listing_keeps_order_and_missing_clubs(synthetic_client: tuple[TestClient, dict]) -> None:
    """Directory order is preserved, duplicates removed and missing records retained with null names."""
    client, routes = synthetic_client
    routes["/country/9/club"] = {"clubIds": ["20", "10", "20", "30"]}
    routes["/clubs"] = [{"id": "10", "name": "Second"}, {"id": "20", "name": "First"}]
    response = client.get("/clubs/?country_id=9")
    assert response.status_code == 200
    body = response.json()
    assert (body["countryId"], body["countryName"]) == (9, "Argentina")
    assert body["clubs"] == [
        {"id": "20", "name": "First"},
        {"id": "10", "name": "Second"},
        {"id": "30", "name": None},
    ]
    assert "updatedAt" in body


def test_country_listing_empty_country(synthetic_client: tuple[TestClient, dict]) -> None:
    """A known country with no listed clubs returns an empty list."""
    client, routes = synthetic_client
    routes["/country/9/club"] = {"clubIds": []}
    response = client.get("/clubs/?country_id=9")
    assert response.status_code == 200
    assert response.json()["clubs"] == []


@pytest.mark.parametrize("directory", [{}, {"clubIds": None}, {"clubIds": "131"}, {"clubIds": {}}, [], None])
def test_country_listing_rejects_malformed_directory(
    synthetic_client: tuple[TestClient, dict], directory: object
) -> None:
    """Malformed upstream directories return 502 instead of a successful empty listing."""
    client, routes = synthetic_client
    routes["/country/9/club"] = directory
    response = client.get("/clubs/?country_id=9")
    assert response.status_code == 502
    assert response.json()["detail"] == "Unexpected upstream payload for /country/9/club"


def test_country_listing_unknown_country(synthetic_client: tuple[TestClient, dict]) -> None:
    """Unknown countries return 404 even though upstream would answer an empty directory."""
    client, _ = synthetic_client
    response = client.get("/clubs/?country_id=999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Country not found: 999999"


@pytest.mark.parametrize("query", ["", "?country_id=0", "?country_id=-1", "?country_id=abc"])
def test_country_listing_validates_country_id(synthetic_client: tuple[TestClient, dict], query: str) -> None:
    """A positive integer country ID is required."""
    client, _ = synthetic_client
    assert client.get(f"/clubs/{query}").status_code == 422


def test_countries_exposes_reference_metadata(synthetic_client: tuple[TestClient, dict]) -> None:
    """Country discovery retains historical entries and metadata, while omitting unrelated attributes."""
    client, routes = synthetic_client
    routes["/attributes"] = {
        "countries": [
            {
                "id": 189,
                "name": "England",
                "fifaCode": "ENG",
                "confederationId": 6,
                "flagUrl": "https://example.com/england.png",
                "isHistorical": False,
                "identifier": "England",
            },
            {"id": 999, "name": "Historical country", "isHistorical": True},
        ],
        "positions": [{"id": 1, "name": "Goalkeeper"}],
    }
    response = client.get("/countries/")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"countries", "updatedAt"}
    assert body["countries"] == [
        {
            "id": 189,
            "name": "England",
            "fifaCode": "ENG",
            "confederationId": 6,
            "flagUrl": "https://example.com/england.png",
            "isHistorical": False,
        },
        {
            "id": 999,
            "name": "Historical country",
            "fifaCode": None,
            "confederationId": None,
            "flagUrl": None,
            "isHistorical": True,
        },
    ]
    routes["/country/189/club"] = {"clubIds": []}
    club_response = client.get("/clubs/?country_id=189")
    assert club_response.status_code == 200
    assert club_response.json()["countryName"] == "England"
