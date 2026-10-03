from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import RedirectResponse, Response

from app.api.api import api_router
from app.settings import settings
from app.tfmkt import TfmktClient
from app.tfmkt.freshness import track_fetches

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMITING_FREQUENCY],
    enabled=settings.RATE_LIMITING_ENABLE,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create the shared tfmkt client on startup and close it on shutdown."""
    app.state.tfmkt = TfmktClient()
    yield
    await app.state.tfmkt.aclose()


app = FastAPI(
    title="Transfermarkt API",
    version="4.0.0",
    description="Football data from Transfermarkt's JSON API: players, clubs and competitions.",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.include_router(api_router)


@app.middleware("http")
async def track_upstream_fetches(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Start a per-request record of upstream fetch times, used for `updatedAt`."""
    track_fetches()
    return await call_next(request)


@app.get("/", include_in_schema=False)
def docs_redirect() -> RedirectResponse:
    """Redirect the root URL to the interactive API docs."""
    return RedirectResponse(url="/docs")


@app.get("/health", include_in_schema=False)
def health() -> dict:
    """Liveness check for the hosting platform. Does not call Transfermarkt."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
