from fastapi import FastAPI
from services.players import TransfermarktPlayers

app = FastAPI()


@app.get("/players/{player_id}/{player_name}")
def get_player_info(player_id: str, player_name: str):
    tfmkt = TransfermarktPlayers(player_id=player_id, player_name=player_name)
    return tfmkt.get_player_info()

