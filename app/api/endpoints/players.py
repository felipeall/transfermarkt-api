from typing import Optional

from fastapi import APIRouter

from app.schemas import players as schemas
from app.services.players.achievements import TransfermarktPlayerAchievements
from app.services.players.injuries import TransfermarktPlayerInjuries
from app.services.players.jersey_numbers import TransfermarktPlayerJerseyNumbers
from app.services.players.market_value import TransfermarktPlayerMarketValue
from app.services.players.profile import TransfermarktPlayerProfile
from app.services.players.search import TransfermarktPlayerSearch
from app.services.players.stats import TransfermarktPlayerStats
from app.services.players.transfers import TransfermarktPlayerTransfers

router = APIRouter()


@router.get("/search/{player_name}", response_model=schemas.PlayerSearch, response_model_exclude_none=True)
def search_players(player_name: str, page_number: Optional[int] = 1):
    tfmkt = TransfermarktPlayerSearch(query=player_name, page_number=page_number)
    found_players = tfmkt.search_players()
    return found_players


@router.get("/{player_id}/profile", response_model=schemas.PlayerProfile, response_model_exclude_none=True)
def get_player_profile(player_id: str):
    tfmkt = TransfermarktPlayerProfile(player_id=player_id)
    player_info = tfmkt.get_player_profile()
    return player_info


@router.get("/{player_id}/market_value", response_model=schemas.PlayerMarketValue, response_model_exclude_none=True)
def get_player_market_value(player_id: str):
    tfmkt = TransfermarktPlayerMarketValue(player_id=player_id)
    player_market_value = tfmkt.get_player_market_value()
    return player_market_value


@router.get("/{player_id}/transfers", response_model=schemas.PlayerTransfers, response_model_exclude_none=True)
def get_player_transfers(player_id: str):
    tfmkt = TransfermarktPlayerTransfers(player_id=player_id)
    player_market_value = tfmkt.get_player_transfers()
    return player_market_value


@router.get("/{player_id}/jersey_numbers", response_model=schemas.PlayerJerseyNumbers, response_model_exclude_none=True)
def get_player_jersey_numbers(player_id: str):
    tfmkt = TransfermarktPlayerJerseyNumbers(player_id=player_id)
    player_jerseynumbers = tfmkt.get_player_jersey_numbers()
    return player_jerseynumbers


@router.get("/{player_id}/stats", response_model=schemas.PlayerStats, response_model_exclude_none=True)
def get_player_stats(player_id: str):
    tfmkt = TransfermarktPlayerStats(player_id=player_id)
    player_stats = tfmkt.get_player_stats()
    return player_stats


@router.get("/{player_id}/injuries", response_model=schemas.PlayerInjuries, response_model_exclude_none=True)
def get_player_injuries(player_id: str, page_number: Optional[int] = 1):
    tfmkt = TransfermarktPlayerInjuries(player_id=player_id, page_number=page_number)
    players_injuries = tfmkt.get_player_injuries()
    return players_injuries


@router.get("/{player_id}/achievements", response_model=schemas.PlayerAchievements, response_model_exclude_none=True)
def get_player_achievements(player_id: str):
    tfmkt = TransfermarktPlayerAchievements(player_id=player_id)
    player_achievements = tfmkt.get_player_achievements()
    return player_achievements
