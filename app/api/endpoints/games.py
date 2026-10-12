from fastapi import APIRouter

from app.api.dependencies import Tfmkt
from transfermarkt_api.schemas.games import Game
from transfermarkt_api.services.games import game

router = APIRouter()


@router.get("/{game_id}", response_model=Game)
async def get_game(game_id: str, tfmkt: Tfmkt) -> dict:
    """Get a match: score, lineups, coaches, stadium and events (goals, cards, substitutions)."""
    return await game.get_game(tfmkt, game_id)
