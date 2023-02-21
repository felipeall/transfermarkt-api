from typing import Optional

from fastapi import APIRouter

from app.services.competitions.clubs import TransfermarktCompetitionClubs

router = APIRouter()


@router.get("/{competition_id}/clubs")
def get_competition_clubs(competition_id: str, season_id: Optional[str] = None):
    tfmkt = TransfermarktCompetitionClubs(competition_id=competition_id, season_id=season_id)
    competition_clubs = tfmkt.get_competition_clubs()
    return competition_clubs
