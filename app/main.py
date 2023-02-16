import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.services.market_value import TransfermarktMarketValue
from app.services.players import TransfermarktPlayers
from app.services.search import TransfermarktPlayerSearch

app = FastAPI()


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/players/{player_name}", tags=["Players"])
def search_players(player_name: str):
    tfmkt = TransfermarktPlayerSearch(query=player_name)
    found_players = tfmkt.search_players()
    return found_players


@app.get("/players/{player_code}/{player_id}", tags=["Players"])
def get_player_info(player_code: str, player_id: str):
    tfmkt = TransfermarktPlayers(player_code=player_code, player_id=player_id)
    player_info = tfmkt.get_player_info()
    return player_info


@app.get("/market_value/{player_code}/{player_id}", tags=["Players"])
def get_player_market_value(player_code: str, player_id: str):
    tfmkt = TransfermarktMarketValue(player_code=player_code, player_id=player_id)
    player_market_value = tfmkt.get_player_market_value()
    return player_market_value


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
