from fastapi import APIRouter

from app.api.dependencies import Tfmkt
from transfermarkt_api.schemas.games import Game

router = APIRouter()


@router.get("/{game_id}")
async def get_game(game_id: str, tfmkt: Tfmkt) -> Game:
    """Get a match: score, lineups, coaches, stadium and events (goals, cards, substitutions)."""
    return await tfmkt.game(game_id)
