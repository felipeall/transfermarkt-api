from typing import Optional

from fastapi import APIRouter, HTTPException

from app.api.params import PageNumber
from app.schemas import players as schemas
from app.schemas.achievements import Achievements
from app.services.players import (
    absences,
    achievements,
    injuries,
    market_value,
    matches,
    national_career,
    profile,
    search,
    stats,
    transfers,
)
from app.tfmkt import Tfmkt

router = APIRouter()

NOT_AVAILABLE = {501: {"description": "No JSON data source available for this endpoint"}}


@router.get("/search/{player_name}", response_model=schemas.PlayerSearch)
async def search_players(player_name: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> dict:
    """Search players by name."""
    return await search.search_players(tfmkt, player_name, page_number)


@router.get("/{player_id}/profile", response_model=schemas.PlayerProfile)
async def get_player_profile(player_id: str, tfmkt: Tfmkt) -> dict:
    """Get a player's profile."""
    return await profile.get_player_profile(tfmkt, player_id)


@router.get("/{player_id}/market_value", response_model=schemas.PlayerMarketValue)
async def get_player_market_value(player_id: str, tfmkt: Tfmkt) -> dict:
    """Get a player's current market value, valuation history and ranking."""
    return await market_value.get_player_market_value(tfmkt, player_id)


@router.get("/{player_id}/transfers", response_model=schemas.PlayerTransfers)
async def get_player_transfers(player_id: str, tfmkt: Tfmkt) -> dict:
    """Get a player's transfer history and youth clubs."""
    return await transfers.get_player_transfers(tfmkt, player_id)


@router.get("/{player_id}/jersey_numbers", responses=NOT_AVAILABLE)
async def get_player_jersey_numbers(player_id: str) -> None:
    """Jersey number history: answers 501, the JSON API has no source for it."""
    raise HTTPException(
        status_code=501,
        detail="Jersey number history is not available: Transfermarkt's JSON API has no equivalent data.",
    )


@router.get("/{player_id}/stats", response_model=schemas.PlayerStats)
async def get_player_stats(player_id: str, tfmkt: Tfmkt) -> dict:
    """Get a player's statistics per season, competition and club."""
    return await stats.get_player_stats(tfmkt, player_id)


@router.get("/{player_id}/matches", response_model=schemas.PlayerMatches)
async def get_player_matches(
    player_id: str,
    tfmkt: Tfmkt,
    page_number: PageNumber = 1,
    season_id: Optional[str] = None,
) -> dict:
    """Get the matches of a player's teams with the player's part in each, most recent first, paginated."""
    return await matches.get_player_matches(tfmkt, player_id, page_number, season_id)


@router.get("/{player_id}/injuries", response_model=schemas.PlayerInjuries)
async def get_player_injuries(player_id: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> dict:
    """Get a player's injury history, paginated."""
    return await injuries.get_player_injuries(tfmkt, player_id, page_number)


@router.get("/{player_id}/absences", response_model=schemas.PlayerAbsences)
async def get_player_absences(player_id: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> dict:
    """Get a player's non-injury absences, paginated."""
    return await absences.get_player_absences(tfmkt, player_id, page_number)


@router.get("/{player_id}/achievements", response_model=Achievements)
async def get_player_achievements(player_id: str, tfmkt: Tfmkt) -> dict:
    """Get a player's titles and awards."""
    return await achievements.get_player_achievements(tfmkt, player_id)


@router.get("/{player_id}/national_career", response_model=schemas.PlayerNationalCareer)
async def get_player_national_career(player_id: str, tfmkt: Tfmkt) -> dict:
    """Get the national teams a player has played for."""
    return await national_career.get_player_national_career(tfmkt, player_id)
