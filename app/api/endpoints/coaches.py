from fastapi import APIRouter

from app.api.params import PageNumber
from app.schemas import coaches as schemas
from app.services.coaches import profile, search
from app.tfmkt import Tfmkt

router = APIRouter()


@router.get("/search/{coach_name}", response_model=schemas.CoachSearch)
async def search_coaches(coach_name: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> dict:
    """Search coaches by name."""
    return await search.search_coaches(tfmkt, coach_name, page_number)


@router.get("/{coach_id}/profile", response_model=schemas.CoachProfile)
async def get_coach_profile(coach_id: str, tfmkt: Tfmkt) -> dict:
    """Get a coach's profile."""
    return await profile.get_coach_profile(tfmkt, coach_id)
