from typing import Optional

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.services.clubs.players import TransfermarktClubPlayers
from app.services.clubs.search import TransfermarktClubSearch
from app.services.players.market_value import TransfermarktPlayerMarketValue
from app.services.players.profile import TransfermarktPlayerProfile
from app.services.players.search import TransfermarktPlayerSearch
from app.services.players.transfers import TransfermarktPlayerTransfers

app = FastAPI()


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/players/search/{player_name}", tags=["Players"])
def search_players(player_name: str):
    tfmkt = TransfermarktPlayerSearch(query=player_name)
    found_players = tfmkt.search_players()
    return found_players


@app.get("/players/{player_id}/profile", tags=["Players"])
def get_player_profile(player_id: str):
    tfmkt = TransfermarktPlayerProfile(player_id=player_id)
    player_info = tfmkt.get_player_profile()
    return player_info


@app.get("/players/{player_id}/market_value", tags=["Players"])
def get_player_market_value(player_id: str):
    tfmkt = TransfermarktPlayerMarketValue(player_id=player_id)
    player_market_value = tfmkt.get_player_market_value()
    return player_market_value


@app.get("/players/{player_id}/transfers", tags=["Players"])
def get_player_transfers(player_id: str):
    tfmkt = TransfermarktPlayerTransfers(player_id=player_id)
    player_market_value = tfmkt.get_player_transfers()
    return player_market_value


@app.get("/clubs/search/{club_name}", tags=["Clubs"])
def search_clubs(club_name: str):
    tfmkt = TransfermarktClubSearch(query=club_name)
    found_clubs = tfmkt.search_clubs()
    return found_clubs


@app.get("/clubs/{club_id}/players", tags=["Clubs"])
def get_club_players(club_id: str, season_year: Optional[str] = None):
    tfmkt = TransfermarktClubPlayers(club_id=club_id, season_id=season_year)
    club_players = tfmkt.get_club_players()
    return club_players


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
