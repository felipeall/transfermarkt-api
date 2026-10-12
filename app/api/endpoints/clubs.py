from typing import Annotated, Optional

from fastapi import APIRouter, Query

from app.api.dependencies import Tfmkt
from app.api.params import PageNumber
from transfermarkt_api.schemas import clubs as schemas
from transfermarkt_api.schemas.achievements import Achievements
from transfermarkt_api.schemas.clubs.listing import ClubListing

router = APIRouter()


@router.get("/")
async def list_clubs(country_id: Annotated[int, Query(gt=0)], tfmkt: Tfmkt) -> ClubListing:
    """List available clubs for a country. Coverage is limited; this is not a complete country directory."""
    return await tfmkt.clubs(country_id)


@router.get("/search/{club_name}", response_model=schemas.ClubSearch)
async def search_clubs(club_name: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> schemas.ClubSearch:
    """Search clubs by name."""
    return await tfmkt.search_clubs(club_name, page_number=page_number)


@router.get("/{club_id}/profile", response_model=schemas.ClubProfile)
async def get_club_profile(club_id: str, tfmkt: Tfmkt) -> schemas.ClubProfile:
    """Get a club's profile."""
    return await tfmkt.club_profile(club_id)


@router.get("/{club_id}/players", response_model=schemas.ClubPlayers)
async def get_club_players(club_id: str, tfmkt: Tfmkt, season_id: Optional[str] = None) -> schemas.ClubPlayers:
    """Get a club's squad for a season (current squad by default)."""
    return await tfmkt.club_players(club_id, season_id=season_id)


@router.get("/{club_id}/achievements")
async def get_club_achievements(club_id: str, tfmkt: Tfmkt) -> Achievements:
    """Get a club's titles by season."""
    return await tfmkt.club_achievements(club_id)
