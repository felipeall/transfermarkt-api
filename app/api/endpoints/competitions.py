from typing import Optional

from fastapi import APIRouter

from app.services.competitions.clubs import TransfermarktCompetitionClubs
from app.services.competitions.search import TransfermarktCompetitionSearch

router = APIRouter()


@router.get("/search/{competition_name}")
def search_competitions(competition_name: str, page_number: Optional[int] = 1) -> dict:
    tfmkt = TransfermarktCompetitionSearch(query=competition_name, page_number=page_number)
    competitions = tfmkt.search_competitions()
    return competitions


@router.get("/{competition_id}/clubs")
def get_competition_clubs(competition_id: str, season_id: Optional[str] = None) -> dict:
    tfmkt = TransfermarktCompetitionClubs(competition_id=competition_id, season_id=season_id)
    competition_clubs = tfmkt.get_competition_clubs()
    return competition_clubs
