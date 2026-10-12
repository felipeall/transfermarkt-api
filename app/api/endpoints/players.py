from typing import Optional

from fastapi import APIRouter

from app.api.dependencies import Tfmkt
from app.api.params import PageNumber
from transfermarkt_api.schemas import players as schemas
from transfermarkt_api.schemas.achievements import Achievements

router = APIRouter()

NOT_AVAILABLE = {501: {"description": "No JSON data source available for this endpoint"}}


@router.get("/search/{player_name}", response_model=schemas.PlayerSearch)
async def search_players(player_name: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> schemas.PlayerSearch:
    """Search players by name."""
    return await tfmkt.search_players(player_name, page_number=page_number)


@router.get("/{player_id}/profile", response_model=schemas.PlayerProfile)
async def get_player_profile(player_id: str, tfmkt: Tfmkt) -> schemas.PlayerProfile:
    """Get a player's profile."""
    return await tfmkt.player_profile(player_id)


@router.get("/{player_id}/market_value", response_model=schemas.PlayerMarketValue)
async def get_player_market_value(player_id: str, tfmkt: Tfmkt) -> schemas.PlayerMarketValue:
    """Get a player's current market value, valuation history and ranking."""
    return await tfmkt.player_market_value(player_id)


@router.get("/{player_id}/transfers", response_model=schemas.PlayerTransfers)
async def get_player_transfers(player_id: str, tfmkt: Tfmkt) -> schemas.PlayerTransfers:
    """Get a player's transfer history and youth clubs."""
    return await tfmkt.player_transfers(player_id)


@router.get("/{player_id}/jersey_numbers", responses=NOT_AVAILABLE)
async def get_player_jersey_numbers(player_id: str, tfmkt: Tfmkt) -> None:
    """Jersey number history: answers 501, the JSON API has no source for it."""
    await tfmkt.player_jersey_numbers(player_id)


@router.get("/{player_id}/stats", response_model=schemas.PlayerStats)
async def get_player_stats(player_id: str, tfmkt: Tfmkt) -> schemas.PlayerStats:
    """Get a player's statistics per season, competition and club."""
    return await tfmkt.player_stats(player_id)


@router.get("/{player_id}/matches", response_model=schemas.PlayerMatches)
async def get_player_matches(
    player_id: str,
    tfmkt: Tfmkt,
    page_number: PageNumber = 1,
    season_id: Optional[str] = None,
) -> schemas.PlayerMatches:
    """Get the matches of a player's teams with the player's part in each, most recent first, paginated."""
    return await tfmkt.player_matches(player_id, page_number=page_number, season_id=season_id)


@router.get("/{player_id}/injuries", response_model=schemas.PlayerInjuries)
async def get_player_injuries(player_id: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> schemas.PlayerInjuries:
    """Get a player's injury history, paginated."""
    return await tfmkt.player_injuries(player_id, page_number=page_number)


@router.get("/{player_id}/absences", response_model=schemas.PlayerAbsences)
async def get_player_absences(player_id: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> schemas.PlayerAbsences:
    """Get a player's non-injury absences, paginated."""
    return await tfmkt.player_absences(player_id, page_number=page_number)


@router.get("/{player_id}/achievements")
async def get_player_achievements(player_id: str, tfmkt: Tfmkt) -> Achievements:
    """Get a player's titles and awards."""
    return await tfmkt.player_achievements(player_id)


@router.get("/{player_id}/national_career", response_model=schemas.PlayerNationalCareer)
async def get_player_national_career(player_id: str, tfmkt: Tfmkt) -> schemas.PlayerNationalCareer:
    """Get the national teams a player has played for."""
    return await tfmkt.player_national_career(player_id)
