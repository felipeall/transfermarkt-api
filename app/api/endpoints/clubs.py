from typing import Optional

from fastapi import APIRouter

from app.services.clubs.players import TransfermarktClubPlayers
from app.services.clubs.search import TransfermarktClubSearch
from app.services.clubs.profile import TransfermarktClubProfile

router = APIRouter()


@router.get("/search/{club_name}")
def search_clubs(club_name: str):
    tfmkt = TransfermarktClubSearch(query=club_name)
    found_clubs = tfmkt.search_clubs()
    return found_clubs


@router.get("/{club_id}/profile")
def get_club_profile(club_id: str):
    tfmkt = TransfermarktClubProfile(club_id=club_id)
    club_profile = tfmkt.get_club_profile()
    return club_profile


@router.get("/{club_id}/players")
def get_club_players(club_id: str, season_year: Optional[str] = None):
    tfmkt = TransfermarktClubPlayers(club_id=club_id, season_id=season_year)
    club_players = tfmkt.get_club_players()
    return club_players
