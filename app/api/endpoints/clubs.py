from typing import Annotated, Optional

from fastapi import APIRouter, Query

from app.api.params import PageNumber
from app.schemas import clubs as schemas
from app.schemas.achievements import Achievements
from app.schemas.clubs.listing import ClubListing
from app.services.clubs import achievements, listing, players, profile, search
from app.tfmkt import Tfmkt

router = APIRouter()


@router.get("/", response_model=ClubListing)
async def list_clubs(country_id: Annotated[int, Query(gt=0)], tfmkt: Tfmkt) -> dict:
    """List available clubs for a country. Coverage is limited; this is not a complete country directory."""
    return await listing.list_clubs(tfmkt, country_id)


@router.get("/search/{club_name}", response_model=schemas.ClubSearch)
async def search_clubs(club_name: str, tfmkt: Tfmkt, page_number: PageNumber = 1) -> dict:
    """Search clubs by name."""
    return await search.search_clubs(tfmkt, club_name, page_number)


@router.get("/{club_id}/profile", response_model=schemas.ClubProfile)
async def get_club_profile(club_id: str, tfmkt: Tfmkt) -> dict:
    """Get a club's profile."""
    return await profile.get_club_profile(tfmkt, club_id)


@router.get("/{club_id}/players", response_model=schemas.ClubPlayers)
async def get_club_players(club_id: str, tfmkt: Tfmkt, season_id: Optional[str] = None) -> dict:
    """Get a club's squad for a season (current squad by default)."""
    return await players.get_club_players(tfmkt, club_id, season_id)


@router.get("/{club_id}/achievements", response_model=Achievements)
async def get_club_achievements(club_id: str, tfmkt: Tfmkt) -> dict:
    """Get a club's titles by season."""
    return await achievements.get_club_achievements(tfmkt, club_id)
