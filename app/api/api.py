from fastapi import APIRouter

from app.api.endpoints import clubs, coaches, competitions, countries, games, players

api_router = APIRouter()
api_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
api_router.include_router(clubs.router, prefix="/clubs", tags=["clubs"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(coaches.router, prefix="/coaches", tags=["coaches"])
api_router.include_router(countries.router, prefix="/countries", tags=["countries"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
