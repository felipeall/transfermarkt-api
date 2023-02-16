import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.services.players import TransfermarktPlayers
from app.services.search import TransfermarktPlayerSearch

app = FastAPI()


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/players/{player_name}", tags=["Players"])
def search_players(player_name: str):
    tfmkt = TransfermarktPlayerSearch(query=player_name)
    return tfmkt.search_player()


@app.get("/players/{player_id}/{player_code}", tags=["Players"])
def get_player_info(player_id: str, player_code: str):
    tfmkt = TransfermarktPlayers(player_id=player_id, player_code=player_code)
    return tfmkt.get_player_info()


if __name__ == "__main__":
    uvicorn.run("server.api:app", host="0.0.0.0", port=8000, reload=True)
