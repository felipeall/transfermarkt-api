from fastapi import APIRouter

from app.api.endpoints import clubs, players

api_router = APIRouter()
api_router.include_router(clubs.router, prefix="/clubs", tags=["clubs"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
