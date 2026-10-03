from typing import Optional

from fastapi import APIRouter

from app.schemas import competitions as schemas
from app.services.competitions import clubs, search
from app.tfmkt import Tfmkt

router = APIRouter()


@router.get("/search/{competition_name}", response_model=schemas.CompetitionSearch)
async def search_competitions(competition_name: str, tfmkt: Tfmkt, page_number: int = 1) -> dict:
    """Search competitions by name."""
    return await search.search_competitions(tfmkt, competition_name, page_number)


@router.get("/{competition_id}/clubs", response_model=schemas.CompetitionClubs)
async def get_competition_clubs(competition_id: str, tfmkt: Tfmkt, season_id: Optional[str] = None) -> dict:
    """Get the clubs of a competition season (current season by default)."""
    return await clubs.get_competition_clubs(tfmkt, competition_id, season_id)
