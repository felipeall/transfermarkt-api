from typing import Optional

from fastapi import APIRouter

from app.api.params import PageNumber
from app.schemas import competitions as schemas
from app.services.competitions import clubs, search, seasons, table
from app.tfmkt import Tfmkt

router = APIRouter()


@router.get("/search/{competition_name}", response_model=schemas.CompetitionSearch)
async def search_competitions(competition_name: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> dict:
    """Search competitions by name."""
    return await search.search_competitions(tfmkt, competition_name, page_number)


@router.get("/{competition_id}/clubs", response_model=schemas.CompetitionClubs)
async def get_competition_clubs(competition_id: str, tfmkt: Tfmkt, season_id: Optional[str] = None) -> dict:
    """Get the clubs of a competition season (current season by default)."""
    return await clubs.get_competition_clubs(tfmkt, competition_id, season_id)


@router.get("/{competition_id}/table", response_model=schemas.CompetitionTable)
async def get_competition_table(competition_id: str, tfmkt: Tfmkt, season_id: Optional[str] = None) -> dict:
    """Get a competition's league table for a season (current season by default)."""
    return await table.get_competition_table(tfmkt, competition_id, season_id)


@router.get("/{competition_id}/seasons", response_model=schemas.CompetitionSeasons)
async def get_competition_seasons(competition_id: str, tfmkt: Tfmkt) -> dict:
    """Get the seasons available for a competition."""
    return await seasons.get_competition_seasons(tfmkt, competition_id)
