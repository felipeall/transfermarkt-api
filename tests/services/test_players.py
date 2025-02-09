import pytest

from app.schemas.players import (
    PlayerAchievements,
    PlayerInjuries,
    PlayerJerseyNumbers,
    PlayerMarketValue,
    PlayerProfile,
    PlayerSearch,
    PlayerStats,
    PlayerTransfers,
)
from app.services.players.achievements import TransfermarktPlayerAchievements
from app.services.players.injuries import TransfermarktPlayerInjuries
from app.services.players.jersey_numbers import TransfermarktPlayerJerseyNumbers
from app.services.players.market_value import TransfermarktPlayerMarketValue
from app.services.players.profile import TransfermarktPlayerProfile
from app.services.players.search import TransfermarktPlayerSearch
from app.services.players.stats import TransfermarktPlayerStats
from app.services.players.transfers import TransfermarktPlayerTransfers


@pytest.mark.parametrize(
    "player_id",
    [
        "3373",  # Ronaldinho
        "8198",  # Cristiano Ronaldo
        "28003",  # Lionel Messi
        "68290",  # Neymar
    ],
)
def test_players_achievements(player_id: str, load_test_data: callable):
    tfmkt = TransfermarktPlayerAchievements(player_id=player_id)
    response = PlayerAchievements.model_validate(tfmkt.get_player_achievements())
    expected = PlayerAchievements.model_validate(load_test_data(f"players/achievements/{player_id}"))

    assert response == expected


@pytest.mark.parametrize(
    "player_id",
    [
        "3373",  # Ronaldinho
        "8198",  # Cristiano Ronaldo
        "28003",  # Lionel Messi
        "68290",  # Neymar
    ],
)
def test_players_injuries(player_id: str, load_test_data: callable):
    tfmkt = TransfermarktPlayerInjuries(player_id=player_id)
    response = PlayerInjuries.model_validate(tfmkt.get_player_injuries())
    expected = PlayerInjuries.model_validate(load_test_data(f"players/injuries/{player_id}"))

    assert response == expected


@pytest.mark.parametrize(
    "player_id",
    [
        "3373",  # Ronaldinho
        "8198",  # Cristiano Ronaldo
        "28003",  # Lionel Messi
        "68290",  # Neymar
    ],
)
def test_players_jersey_numbers(player_id: str, load_test_data: callable):
    tfmkt = TransfermarktPlayerJerseyNumbers(player_id=player_id)
    response = PlayerJerseyNumbers.model_validate(tfmkt.get_player_jersey_numbers())
    expected = PlayerJerseyNumbers.model_validate(load_test_data(f"players/jersey_numbers/{player_id}"))

    assert response == expected


@pytest.mark.parametrize(
    "player_id",
    [
        "3373",  # Ronaldinho
        "8198",  # Cristiano Ronaldo
        "28003",  # Lionel Messi
        "68290",  # Neymar
    ],
)
def test_players_market_value(player_id: str, load_test_data: callable):
    tfmkt = TransfermarktPlayerMarketValue(player_id=player_id)
    response = PlayerMarketValue.model_validate(tfmkt.get_player_market_value())
    expected = PlayerMarketValue.model_validate(load_test_data(f"players/market_value/{player_id}"))

    assert response == expected


@pytest.mark.parametrize(
    "player_id",
    [
        "3373",  # Ronaldinho
        "8198",  # Cristiano Ronaldo
        "28003",  # Lionel Messi
        "68290",  # Neymar
    ],
)
def test_players_profile(player_id: str):
    tfmkt = TransfermarktPlayerProfile(player_id=player_id)
    response = PlayerProfile.model_validate(tfmkt.get_player_profile())
    expected = PlayerProfile.model_validate(load_test_data(f"players/profile/{player_id}"))

    assert response == expected


@pytest.mark.parametrize(
    "query",
    [
        "Ronaldo",
        "Messi",
        "Neymar",
        "Cristiano",
    ],
)
def test_players_search(query: str, load_test_data: callable):
    tfmkt = TransfermarktPlayerSearch(query=query)
    response = PlayerSearch.model_validate(tfmkt.search_players())
    expected = PlayerSearch.model_validate(load_test_data(f"players/search/{query}"))

    assert response == expected


@pytest.mark.parametrize(
    "player_id",
    [
        "3373",  # Ronaldinho
        "8198",  # Cristiano Ronaldo
        "28003",  # Lionel Messi
        "68290",  # Neymar
    ],
)
def test_players_stats(player_id: str, load_test_data: callable):
    tfmkt = TransfermarktPlayerStats(player_id=player_id)
    response = PlayerStats.model_validate(tfmkt.get_player_stats())
    expected = PlayerStats.model_validate(load_test_data(f"players/stats/{player_id}"))

    assert response == expected


@pytest.mark.parametrize(
    "player_id",
    [
        "3373",  # Ronaldinho
        "8198",  # Cristiano Ronaldo
        "28003",  # Lionel Messi
        "68290",  # Neymar
    ],
)
def test_players_transfers(player_id: str, load_test_data: callable):
    tfmkt = TransfermarktPlayerTransfers(player_id=player_id)
    response = PlayerTransfers.model_validate(tfmkt.get_player_transfers())
    expected = PlayerTransfers.model_validate(load_test_data(f"players/transfers/{player_id}"))

    assert response == expected
