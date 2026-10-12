from typing import Optional

from fastapi import APIRouter

from app.api.dependencies import Tfmkt
from app.api.params import PageNumber
from transfermarkt_api.schemas import competitions as schemas

router = APIRouter()


@router.get("/search/{competition_name}", response_model=schemas.CompetitionSearch)
async def search_competitions(
    competition_name: str, tfmkt: Tfmkt, page_number: PageNumber = 1
) -> schemas.CompetitionSearch:
    """Search competitions by name."""
    return await tfmkt.search_competitions(competition_name, page_number=page_number)


@router.get("/{competition_id}/clubs", response_model=schemas.CompetitionClubs)
async def get_competition_clubs(
    competition_id: str, tfmkt: Tfmkt, season_id: Optional[str] = None
) -> schemas.CompetitionClubs:
    """Get the clubs of a competition season (current season by default)."""
    return await tfmkt.competition_clubs(competition_id, season_id=season_id)


@router.get("/{competition_id}/table", response_model=schemas.CompetitionTable)
async def get_competition_table(
    competition_id: str, tfmkt: Tfmkt, season_id: Optional[str] = None
) -> schemas.CompetitionTable:
    """Get a competition's league table for a season (current season by default)."""
    return await tfmkt.competition_table(competition_id, season_id=season_id)


@router.get("/{competition_id}/seasons", response_model=schemas.CompetitionSeasons)
async def get_competition_seasons(competition_id: str, tfmkt: Tfmkt) -> schemas.CompetitionSeasons:
    """Get the seasons available for a competition."""
    return await tfmkt.competition_seasons(competition_id)
