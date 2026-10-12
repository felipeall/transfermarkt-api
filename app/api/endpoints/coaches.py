from fastapi import APIRouter

from app.api.dependencies import Tfmkt
from app.api.params import PageNumber
from transfermarkt_api.schemas import coaches as schemas

router = APIRouter()


@router.get("/search/{coach_name}", response_model=schemas.CoachSearch)
async def search_coaches(coach_name: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> schemas.CoachSearch:
    """Search coaches by name."""
    return await tfmkt.search_coaches(coach_name, page_number=page_number)


@router.get("/{coach_id}/profile", response_model=schemas.CoachProfile)
async def get_coach_profile(coach_id: str, tfmkt: Tfmkt) -> schemas.CoachProfile:
    """Get a coach's profile."""
    return await tfmkt.coach_profile(coach_id)
