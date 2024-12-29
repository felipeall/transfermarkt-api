from typing import Optional

from fastapi import APIRouter

from app.schemas import clubs as schemas
from app.services.clubs.players import TransfermarktClubPlayers
from app.services.clubs.profile import TransfermarktClubProfile
from app.services.clubs.search import TransfermarktClubSearch

router = APIRouter()


@router.get("/search/{club_name}", response_model=schemas.ClubSearch, response_model_exclude_none=True)
def search_clubs(club_name: str, page_number: Optional[int] = 1) -> dict:
    tfmkt = TransfermarktClubSearch(query=club_name, page_number=page_number)
    found_clubs = tfmkt.search_clubs()
    return found_clubs


@router.get("/{club_id}/profile", response_model=schemas.ClubProfile, response_model_exclude_defaults=True)
def get_club_profile(club_id: str) -> dict:
    tfmkt = TransfermarktClubProfile(club_id=club_id)
    club_profile = tfmkt.get_club_profile()
    return club_profile


@router.get("/{club_id}/players", response_model=schemas.ClubPlayers, response_model_exclude_defaults=True)
def get_club_players(club_id: str, season_id: Optional[str] = None) -> dict:
    tfmkt = TransfermarktClubPlayers(club_id=club_id, season_id=season_id)
    club_players = tfmkt.get_club_players()
    return club_players
