import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.api.api import api_router

app = FastAPI(title="Transfermarkt API")
app.include_router(api_router)


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
