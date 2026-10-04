from fastapi import APIRouter

from app.schemas.games import Game
from app.services.games import game
from app.tfmkt import Tfmkt

router = APIRouter()


@router.get("/{game_id}", response_model=Game)
async def get_game(game_id: str, tfmkt: Tfmkt) -> dict:
    """Get a match: score, lineups, coaches, stadium and events (goals, cards, substitutions)."""
    return await game.get_game(tfmkt, game_id)
