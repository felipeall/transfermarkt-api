from fastapi import FastAPI
from services.players import TransfermarktPlayers
from services.search import TransfermarktPlayerSearch

app = FastAPI()


@app.get("/players/{player_id}/{player_code}")
def get_player_info(player_id: str, player_code: str):
    tfmkt = TransfermarktPlayers(player_id=player_id, player_code=player_code)
    return tfmkt.get_player_info()


@app.get("/players/{query}")
def search_players(query: str):
    tfmkt = TransfermarktPlayerSearch(query=query)
    return tfmkt.search_player()
