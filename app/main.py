from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.services.players import TransfermarktPlayers
from app.services.search import TransfermarktPlayerSearch

app = FastAPI()


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/players/{query}", tags=["Players"])
def search_players(query: str):
    tfmkt = TransfermarktPlayerSearch(query=query)
    return tfmkt.search_player()


@app.get("/players/{player_id}/{player_code}", tags=["Players"])
def get_player_info(player_id: str, player_code: str):
    tfmkt = TransfermarktPlayers(player_id=player_id, player_code=player_code)
    return tfmkt.get_player_info()
