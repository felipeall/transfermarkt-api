from fastapi import FastAPI

app = FastAPI()


@app.get("/players/{player_url}")
def get_player_info():
    return {"message": "Hello World"}
