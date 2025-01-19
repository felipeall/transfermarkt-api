import pytest

from app.services.competitions.clubs import TransfermarktCompetitionClubs
from app.services.competitions.search import TransfermarktCompetitionSearch


@pytest.mark.parametrize(
    "competition_id",
    [
        "BRA1",
        "GB1",
        "ES1",
    ],
)
def test_competitions_clubs(competition_id: str, load_test_data: callable):
    tfmkt = TransfermarktCompetitionClubs(competition_id=competition_id)
    response = tfmkt.get_competition_clubs()
    expected = load_test_data(f"competitions/clubs/{competition_id}")

    assert response == expected


@pytest.mark.parametrize(
    "query",
    [
        "Brasileirão",
        "Premier League",
        "La Liga",
    ],
)
def test_competitions_search(query: str, load_test_data: callable):
    tfmkt = TransfermarktCompetitionSearch(query=query)
    response = tfmkt.search_competitions()
    expected = load_test_data(f"competitions/search/{query}")

    assert response == expected
