import pytest

from app.services.clubs.players import TransfermarktClubPlayers
from app.services.clubs.profile import TransfermarktClubProfile
from app.services.clubs.search import TransfermarktClubSearch


@pytest.mark.parametrize(
    "club_id, season_id",
    [
        ("5", "2003"),  # Milan AC
        ("27", "2019"),  # FC Bayern Munich
        ("31", "2018"),  # Liverpool FC
        ("131", "2010"),  # Barcelona FC
        ("131", None),  # Barcelona FC
        ("210", "2017"),  # Grêmio FBPA
    ],
)
def test_club_players(club_id: str, season_id: str, load_test_data: callable):
    tfmkt = TransfermarktClubPlayers(club_id=club_id, season_id=season_id)
    response = tfmkt.get_club_players()
    expected = load_test_data(f"clubs/players/{club_id}_{season_id}")

    assert response == expected


@pytest.mark.parametrize(
    "club_id",
    [
        "5",  # Milan AC
        "27",  # FC Bayern Munich
        "31",  # Liverpool FC
        "131",  # Barcelona FC
        "210",  # Grêmio FBPA
    ],
)
def test_clubs_profile(club_id: str, load_test_data: callable):
    tfmkt = TransfermarktClubProfile(club_id=club_id)
    response = tfmkt.get_club_profile()
    expected = load_test_data(f"clubs/profile/{club_id}")

    assert response == expected


@pytest.mark.parametrize(
    "query",
    [
        "Milan",
        "Bayern",
        "Liverpool",
        "Barcelona",
        "Grêmio",
    ],
)
def test_clubs_search(query: str, load_test_data: callable):
    tfmkt = TransfermarktClubSearch(query=query)
    response = tfmkt.search_clubs()
    expected = load_test_data(f"clubs/search/{query}")

    assert response == expected
