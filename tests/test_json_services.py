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


def test_club_profile_richer_data(client: TestClient) -> None:
    """Recorded club data exposes exact squad values, historical names and the full stadium."""
    response = client.get("/clubs/131/profile")
    assert response.status_code == 200
    body = response.json()
    assert (body["shortName"], body["abbreviation"], body["clubCode"]) == ("Barcelona", "Barça", "BAR")
    assert body["squad"]["domesticPlayers"] == 14
    assert body["squad"]["averageMarketValue"] == 46762964
    assert body["squad"]["acquisitionValue"] == 489500000
    assert body["squad"]["top18PlayersMarketValue"] == 1204000000
    assert body["squad"]["top18SharePercentage"] == 95.36
    assert {"name": "CF Barcelona", "shortName": "Barcelona", "abbreviation": "Barça", "seasonId": "1972"} in body[
        "historicalNames"
    ]
    stadium = body["stadium"]
    assert stadium["name"] == body["stadiumName"] == "Spotify Camp Nou"
    assert stadium["capacity"] == body["stadiumSeats"] == 62657
    assert stadium["internationalCapacity"] == 62657
    assert stadium["countryName"] == "Spain"
    assert (stadium["latitude"], stadium["longitude"]) == (41.380896, 2.1228198)
    assert (stadium["buildYear"], stadium["renovationYear"]) == (1957, 1994)
    assert (stadium["fieldLength"], stadium["fieldWidth"], stadium["fieldSurface"]) == (105, 68, "Hybridrasen")
    assert stadium["website"] == "www.fcbarcelona.com/web/index_idiomes.html"
    assert len(stadium["images"]) == 7


@pytest.mark.parametrize("has_stadium", [False, True])
def test_club_profile_missing_optional_details(
    synthetic_client: tuple[TestClient, dict],
    has_stadium: bool,
) -> None:
    """Absent details stay nullable; meaningful zeros and stadium coordinates survive."""
    client, routes = synthetic_client
    routes["/club/1"] = {
        "id": "1",
        "name": "Club",
        "squadDetails": {"acquisitionValue": {"value": 0}, "top18SharePercentage": {"value": 0}},
    }
    routes["/club/1/squad"] = {"squad": [], "localCount": 0}
    if has_stadium:
        routes["/club/1/stadium"] = {
            "id": "2",
            "capacity": 0,
            "internationalCapacity": 0,
            "location": {"latitude": 0, "longitude": 0},
            "buildingDetails": {"buildYear": 0, "renovationYear": 0, "fieldSurface": ""},
            "images": [{"url": "https://example.test/stadium.jpg"}, {"url": "https://example.test/stadium.jpg"}, {}],
        }
    response = client.get("/clubs/1/profile")
    assert response.status_code == 200
    body = response.json()
    assert body["shortName"] is None
    assert body["abbreviation"] is None
    assert body["clubCode"] is None
    assert body["historicalNames"] == []
    assert body["squad"]["domesticPlayers"] == 0
    assert body["squad"]["acquisitionValue"] == 0
    assert body["squad"]["averageMarketValue"] is None
    assert body["squad"]["top18PlayersMarketValue"] is None
    assert body["squad"]["top18SharePercentage"] == 0
    if has_stadium:
        assert body["stadium"]["capacity"] == 0
        assert body["stadium"]["latitude"] == body["stadium"]["longitude"] == 0
        assert body["stadium"]["buildYear"] is None
        assert body["stadium"]["website"] is None
        assert body["stadium"]["fieldSurface"] is None
        assert body["stadium"]["images"] == ["https://example.test/stadium.jpg"]
    else:
        assert body["stadium"] is None


@pytest.mark.parametrize("season_id", [None, "2014"])
def test_squad_role_comes_from_selected_season(
    synthetic_client: tuple[TestClient, dict],
    season_id: str | None,
) -> None:
    """Shirt numbers and captaincy come from the selected squad even without a player record."""
    client, routes = synthetic_client
    routes["/club/1/squad"] = {
        "squad": [
            {"playerId": "10", "type": "historical" if season_id else "current", "shirtNumber": 8, "isCaptain": True},
            {"playerId": "11", "type": "historical" if season_id else "current", "shirtNumber": 0, "isCaptain": False},
            {"playerId": "12", "type": "historical" if season_id else "current"},
        ],
    }
    routes["/players"] = [
        {
            "id": "10",
            "name": "Player",
            "clubAssignment": {"clubId": "2", "shirtNumber": 99, "isCaptain": False},
        }
    ]
    response = client.get("/clubs/1/players", params={"season_id": season_id} if season_id else {})
    assert response.status_code == 200
    players = response.json()["players"]
    assert [(p["shirtNumber"], p["isCaptain"]) for p in players] == [(8, True), (0, False), (None, None)]


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


@pytest.mark.parametrize(
    "path",
    [
        "/players/search/x?page_number=0",
        "/players/7/injuries?page_number=-1",
        "/players/7/absences?page_number=0",
        "/clubs/search/x?page_number=0",
        "/coaches/search/x?page_number=0",
        "/competitions/search/x?page_number=0",
    ],
)
def test_page_number_below_one_is_rejected(synthetic_client: tuple[TestClient, dict], path: str) -> None:
    """Page numbers start at 1; lower values answer 422 instead of slicing from the end of the list."""
    client, _ = synthetic_client

    assert client.get(path).status_code == 422


def test_current_squad_with_non_current_members(synthetic_client: tuple[TestClient, dict]) -> None:
    """A current squad listing members of another type is served as a past-style squad instead of failing."""
    client, routes = synthetic_client
    routes["/club/1/squad"] = {"clubId": "1", "squad": [{"playerId": "10", "type": "loan"}]}
    routes["/players"] = [{"id": "10", "name": "Loaned Player"}]

    response = client.get("/clubs/1/players")

    assert response.status_code == 200
    assert [p["name"] for p in response.json()["players"]] == ["Loaned Player"]


def test_national_team_confederation_with_string_country_id(synthetic_client: tuple[TestClient, dict]) -> None:
    """Country IDs sent as strings still resolve the national team's confederation."""
    client, routes = synthetic_client
    routes["/attributes"] = {
        "countries": [{"id": 9, "name": "Argentina", "confederationId": 3}],
        "confederations": [{"id": 3, "name": "CONMEBOL"}],
    }
    routes["/club/3437"] = {
        "id": "3437",
        "name": "Argentina",
        "baseDetails": {"isNationalTeam": True, "countryId": "9"},
    }
    routes["/club/3437/squad"] = {"clubId": "3437", "squad": []}

    body = client.get("/clubs/3437/profile").json()

    assert body["confederation"] == "CONMEBOL"


@pytest.mark.parametrize("attributes", [{}, {"countries": "Argentina"}, {"countries": ["Argentina"]}])
def test_countries_with_malformed_reference_data_are_502(
    synthetic_client: tuple[TestClient, dict],
    attributes: dict,
) -> None:
    """A reference payload without a list of country records is an upstream error, not a server error."""
    client, routes = synthetic_client
    routes["/attributes"] = attributes

    assert client.get("/countries/").status_code == 502


def keeper_game(minutes: int, conceded_on_pitch: int, opponent_total: int) -> dict:
    """A Bundesliga match record for a goalkeeper of club 27."""
    return {
        "gameInformation": {"competitionTypeId": 1, "seasonId": 2025, "competitionId": "L1"},
        "clubsInformation": {"club": {"clubId": 27, "opponentGoalsTotal": opponent_total}},
        "statistics": {
            "generalStatistics": {"participationState": "played" if minutes else "not_in_squad"},
            "cardStatistics": {},
            "goalStatistics": {"goalsScoredTotal": 0, "assists": 0, "opponentGoalsOnThePitch": conceded_on_pitch},
            "playingTimeStatistics": {"playedMinutes": minutes},
        },
    }


def test_goalkeeper_stats_follow_the_website(synthetic_client: tuple[TestClient, dict]) -> None:
    """Goals conceded count only while on the pitch; a clean sheet is a played match the opponent did not score in."""
    client, routes = synthetic_client
    routes["/player/7/performance-game"] = {
        "performance": [
            keeper_game(minutes=90, conceded_on_pitch=0, opponent_total=0),  # clean sheet
            keeper_game(minutes=90, conceded_on_pitch=2, opponent_total=2),
            keeper_game(minutes=45, conceded_on_pitch=0, opponent_total=1),  # conceded after being replaced
            keeper_game(minutes=0, conceded_on_pitch=0, opponent_total=0),  # did not play
        ],
    }

    stat = client.get("/players/7/stats").json()["stats"][0]

    assert (stat["appearances"], stat["goalsConceded"], stat["cleanSheets"]) == (3, 2, 1)


@pytest.mark.parametrize(
    ("upstream_type", "fee_label", "expected"),
    [
        ("STANDARD", "Free Transfer", "freeTransfer"),
        ("STANDARD", "-", "transfer"),
        ("STANDARD", "?", "transfer"),
        ("INTERNAL_TRANSFER", "-", "internal"),
        ("ACTIVE_LOAN_TRANSFER", "Loan fee", "loan"),
        ("RETURNED_FROM_PREVIOUS_LOAN", None, "endOfLoan"),
        ("SOMETHING_NEW", None, None),
    ],
)
def test_transfer_types(
    synthetic_client: tuple[TestClient, dict],
    upstream_type: str,
    fee_label: str | None,
    expected: str | None,
) -> None:
    """Upstream transfer types map to transferType; an unknown fee is never a free transfer."""
    client, routes = synthetic_client
    routes["/player/7"] = {"id": "7", "attributes": {}}
    routes["/transfer/history/player/7"] = {
        "history": {
            "terminated": [
                {
                    "id": "1",
                    "typeDetails": {"type": upstream_type},
                    "transferSource": {"clubId": "2"},
                    "transferDestination": {"clubId": "3"},
                    "details": {"fee": {"value": None, "compact": {"content": fee_label}}},
                },
            ],
        },
    }

    transfer = client.get("/players/7/transfers").json()["transfers"][0]

    assert transfer["transferType"] == expected
    assert transfer["fee"] is None


def test_transfer_details_use_historical_club_context(synthetic_client: tuple[TestClient, dict]) -> None:
    """Transfers retain their recorded league, country and contract data rather than today's club context."""
    client, routes = synthetic_client
    routes["/attributes"]["countries"].append({"id": 157, "name": "Spain"})
    routes["/player/7"] = {"id": "7", "attributes": {}}
    routes["/clubs"] = [
        {"id": "2", "name": "Old club", "baseDetails": {"primaryCompetitionId": "NEW", "countryId": 157}},
        {"id": "3", "name": "New club"},
    ]
    routes["/competitions"] = [{"id": "OLD", "name": "Former league"}]
    routes["/transfer/history/player/7"] = {
        "history": {
            "pending": [
                {
                    "id": "2",
                    "transferSource": {"clubId": "2", "competitionId": "OLD", "countryId": 9},
                    "transferDestination": {"clubId": "3", "competitionId": "MISSING", "countryId": 157},
                    "details": {
                        "isPending": True,
                        "age": 30,
                        "contractUntilDate": "2028-06-30T00:00:00+02:00",
                        "remainingContractPeriod": {"days": 0},
                    },
                }
            ],
            "terminated": [
                {
                    "id": "1",
                    "transferSource": {"clubId": "2"},
                    "transferDestination": {"clubId": "3"},
                    "details": {
                        "age": 22,
                        "contractUntilDate": "2026-06-30T00:00:00+02:00",
                        "remainingContractPeriod": {"days": 729},
                    },
                }
            ],
        }
    }
    response = client.get("/players/7/transfers")
    assert response.status_code == 200
    pending, completed = response.json()["transfers"]
    assert pending["upcoming"] is True
    assert (pending["age"], pending["contractUntil"], pending["remainingContractDays"]) == (30, "2028-06-30", 0)
    assert pending["clubFrom"] == {
        "id": "2",
        "name": "Old club",
        "countryId": "9",
        "countryName": "Argentina",
        "league": {"id": "OLD", "name": "Former league"},
    }
    assert pending["clubTo"] == {
        "id": "3",
        "name": "New club",
        "countryId": "157",
        "countryName": "Spain",
        "league": {"id": "MISSING", "name": None},
    }
    assert (completed["age"], completed["contractUntil"], completed["remainingContractDays"]) == (22, "2026-06-30", 729)
    assert completed["clubFrom"]["league"] is None
    assert completed["clubFrom"]["countryId"] is None
    assert completed["clubFrom"]["countryName"] is None


def test_transfer_extra_details_missing(synthetic_client: tuple[TestClient, dict]) -> None:
    """Absent transfer details remain null, including a missing country or league record."""
    client, routes = synthetic_client
    routes["/player/7"] = {"id": "7"}
    routes["/transfer/history/player/7"] = {
        "history": {
            "terminated": [
                {
                    "id": "1",
                    "transferSource": {"clubId": "2", "countryId": 999},
                    "transferDestination": {"clubId": "3"},
                    "details": {},
                }
            ]
        }
    }
    response = client.get("/players/7/transfers")
    assert response.status_code == 200
    transfer = response.json()["transfers"][0]
    assert transfer["age"] is None
    assert transfer["contractUntil"] is None
    assert transfer["remainingContractDays"] is None
    assert transfer["clubFrom"]["countryId"] == "999"
    assert transfer["clubFrom"]["countryName"] is None
    assert transfer["clubFrom"]["league"] is None


def test_squad_includes_player_images(synthetic_client: tuple[TestClient, dict]) -> None:
    """Squad entries carry the player's portrait, or null when upstream has none."""
    client, routes = synthetic_client
    routes["/club/1/squad"] = {
        "clubId": "1",
        "squad": [{"playerId": "10", "type": "current"}, {"playerId": "11", "type": "current"}],
    }
    routes["/players"] = [
        {"id": "10", "name": "Pictured", "portraitUrl": "https://img.a.transfermarkt.technology/portrait/big/10.jpg"},
        {"id": "11", "name": "Unpictured"},
    ]

    players = client.get("/clubs/1/players").json()["players"]

    assert [p["imageUrl"] for p in players] == ["https://img.a.transfermarkt.technology/portrait/big/10.jpg", None]


def test_profile_extra_fields_edge_cases(synthetic_client: tuple[TestClient, dict]) -> None:
    """Unknown or invalid upstream values for the extra profile fields become null instead of failing."""
    client, routes = synthetic_client
    routes["/player/7"] = {
        "id": "7",
        "name": "Historic Player",
        "lifeDates": {"dateOfDeath": "1990-01-01", "isDateOfDeathUnknown": True},
        "attributes": {"lastContractRenewal": {"year": 2025, "month": 2, "day": 30}},
        "marketValueDetails": {
            "current": {"value": 0, "determined": "2020-01-01"},
            "delta": {"type": "SOMETHING_NEW"},
            "highest": {"value": 0},
        },
        "clubAssignments": [{"type": "current", "clubId": "1", "isCaptain": False}],
    }

    body = client.get("/players/7/profile").json()

    assert body["dateOfDeath"] is None
    assert body["club"]["lastContractRenewal"] is None
    assert body["club"]["isCaptain"] is False
    assert body["nationalTeam"] is None
    assert body["marketValueDetails"] == {
        "lastUpdated": "2020-01-01",
        "trend": None,
        "previous": None,
        "highest": None,
    }


def test_game_events_and_lineups(synthetic_client: tuple[TestClient, dict]) -> None:
    """Events come in match order with card colours, goal assists and substitution direction resolved."""
    client, routes = synthetic_client
    side = {"lineup": {"players": [{"id": "10", "shirtNumber": 1, "isCaptain": True}], "substitutes": []}}
    routes["/game/5"] = {
        "id": "5",
        "baseDetails": {"competitionId": "L1", "seasonId": 2025, "gameDay": 3},
        "homeClub": {"clubId": "1", **side},
        "awayClub": {"clubId": "2", "lineup": {"players": [], "substitutes": []}},
        "score": {"home": 1, "away": 0},
        "actions": [
            {"type": "SUBSTITUTE", "minute": 80, "clubId": "1", "activePlayerId": "10", "passivePlayerId": "11"},
            {"type": "PLACEHOLDER", "minute": 90},
            {"type": "CARD", "minute": 30, "clubId": "2", "activePlayerId": "20", "details": {"seasonYellowCard": 1}},
            {
                "type": "CARD",
                "minute": 60,
                "clubId": "2",
                "activePlayerId": "21",
                "details": {"seasonYellowRedCard": 1},
            },
            {
                "type": "GOAL",
                "minute": 10,
                "clubId": "1",
                "activePlayerId": "10",
                "passivePlayerId": "11",
                "score": {"home": 1, "away": 0},
            },
        ],
    }
    routes["/players"] = [{"id": "10", "name": "Starter"}, {"id": "11", "name": "Sub"}]
    routes["/clubs"] = [{"id": "1", "name": "Home FC"}, {"id": "2", "name": "Away FC"}]

    body = client.get("/games/5").json()

    assert (body["home"]["name"], body["home"]["score"], body["away"]["score"]) == ("Home FC", 1, 0)
    assert body["home"]["startingLineup"][0] == {
        "id": "10",
        "name": "Starter",
        "shirtNumber": 1,
        "position": None,
        "isCaptain": True,
    }
    events = [(e["type"], e["minute"], e["card"]) for e in body["events"]]
    assert events == [
        ("goal", 10, None),
        ("card", 30, "yellow"),
        ("card", 60, "secondYellow"),
        ("substitution", 80, None),
    ]
    goal, substitution = body["events"][0], body["events"][-1]
    assert (goal["player"]["name"], goal["relatedPlayer"]["name"], goal["score"]) == (
        "Starter",
        "Sub",
        {"home": 1, "away": 0},
    )
    assert (substitution["player"]["id"], substitution["relatedPlayer"]["id"]) == ("10", "11")  # off, on


def match_record(game_id: str, date: str, season_id: int, state: str) -> dict:
    """A performance-game record of player 7 for club 1 against club 2."""
    return {
        "gameInformation": {
            "gameId": game_id,
            "competitionId": "L1",
            "competitionTypeId": 1,
            "seasonId": season_id,
            "date": {"dateTimeUTC": date},
        },
        "clubsInformation": {
            "club": {"clubId": "1", "venue": "home", "goalsTotal": 2},
            "opponent": {"clubId": "2", "goalsTotal": 1},
        },
        "statistics": {
            "generalStatistics": {"participationState": state},
            "cardStatistics": {"yellowCard": state == "played"},
            "goalStatistics": {"goalsScoredTotal": 1 if state == "played" else 0},
            "playingTimeStatistics": {"playedMinutes": 90 if state == "played" else 0, "isStarting": state == "played"},
        },
    }


def test_player_matches(synthetic_client: tuple[TestClient, dict]) -> None:
    """Matches are most recent first, filtered by season, with participation in API terms."""
    client, routes = synthetic_client
    routes["/player/7/performance-game"] = {
        "performance": [
            match_record("1", "2024-08-01T18:00:00+00:00", 2024, "played"),
            match_record("2", "2025-08-01T18:00:00+00:00", 2025, "in squad"),
            match_record("3", "2025-09-01T18:00:00+00:00", 2025, "not in squad"),
        ],
    }
    routes["/clubs"] = [{"id": "1", "name": "Club"}, {"id": "2", "name": "Opponent"}]

    all_matches = client.get("/players/7/matches").json()["matches"]
    season = client.get("/players/7/matches?season_id=2024").json()["matches"]

    assert [(m["gameId"], m["participation"]) for m in all_matches] == [
        ("3", "notInSquad"),
        ("2", "onBench"),
        ("1", "played"),
    ]
    assert len(season) == 1
    assert {k: season[0][k] for k in ("opponent", "venue", "clubGoals", "goals", "yellowCard", "isStarting")} == {
        "opponent": {"id": "2", "name": "Opponent"},
        "venue": "home",
        "clubGoals": 2,
        "goals": 1,
        "yellowCard": True,
        "isStarting": True,
    }


def test_game_team_stats(synthetic_client: tuple[TestClient, dict]) -> None:
    """Team statistics are mapped when upstream has them, and null when it does not."""
    client, routes = synthetic_client
    lineup = {"lineup": {"players": [], "substitutes": []}}
    routes["/game/6"] = {
        "id": "6",
        "baseDetails": {"competitionId": "L1"},
        "homeClub": {
            "clubId": "1",
            **lineup,
            "clubStatistics": {
                "gameStatistics": {"possessionPercentage": 61.5, "yellowCards": 2},
                "goalStatistics": {"totalShotAttempts": 12, "onTargetShotAttempts": 4},
                "passingStatistics": {"totalPasses": 500, "accuratePasses": 450},
                "penaltyStatistics": {"freeKicksConcededFromFouls": 9, "freeKicksWonFromFouls": 11},
            },
        },
        "awayClub": {"clubId": "2", **lineup},
        "actions": [],
    }

    body = client.get("/games/6").json()

    stats = body["home"]["stats"]
    assert (stats["possession"], stats["shots"], stats["shotsOnTarget"], stats["passes"]) == (61.5, 12, 4, 500)
    assert (stats["foulsCommitted"], stats["foulsSuffered"], stats["yellowCards"]) == (9, 11, 2)
    assert stats["clearances"] is None
    assert body["away"]["stats"] is None


def test_player_match_role_and_detailed_stats(synthetic_client: tuple[TestClient, dict]) -> None:
    """Each match carries the player's shirt, position, substitution minutes and detailed stats when recorded."""
    client, routes = synthetic_client
    routes["/attributes"] = {"positions": [{"id": 12, "name": "Right Winger"}]}
    record = match_record("1", "2024-08-01T18:00:00+00:00", 2024, "played")
    record["clubsInformation"]["club"]["points"] = 3
    record["statistics"]["generalStatistics"] |= {"shirtNumber": 10, "isCaptain": True, "positionId": 12}
    record["statistics"]["playingTimeStatistics"]["substitutedOut"] = {"minute": 80}
    record["statistics"]["goalStatistics"] |= {"scoringAttempts": 6, "scoringAttemptsOnGoal": 4}
    record["statistics"]["distributionStatistics"] = {"passes": 37, "passesReached": 30}
    record["statistics"]["duelStatistics"] = {"tacklesWon": 2, "foulsGained": 1}
    old_record = match_record("2", "2014-08-01T18:00:00+00:00", 2014, "played")
    routes["/player/7/performance-game"] = {"performance": [record, old_record]}

    recent, old = client.get("/players/7/matches").json()["matches"]

    assert {
        k: recent[k]
        for k in ("shirtNumber", "isCaptain", "position", "substitutedOutMinute", "teamPoints", "shots", "passes")
    } == {
        "shirtNumber": 10,
        "isCaptain": True,
        "position": "Right Winger",
        "substitutedOutMinute": 80,
        "teamPoints": 3,
        "shots": 6,
        "passes": 37,
    }
    assert (recent["accuratePasses"], recent["tacklesWon"], recent["foulsSuffered"]) == (30, 2, 1)
    assert (old["passes"], old["shots"], old["position"]) == (None, None, None)
