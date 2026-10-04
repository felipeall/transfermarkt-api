import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse, RedirectResponse, Response

from app.api.api import api_router
from app.rate_limit import RateLimiter
from app.settings import settings
from app.tfmkt import TfmktClient
from app.tfmkt.freshness import track_fetches

access_log = logging.getLogger("uvicorn.error")


def client_ip(request: Request) -> str:
    """
    Address of the client calling the API, the key for rate limiting.

    On Fly.io, the proxy sets `Fly-Client-IP` to the address that connected to it, replacing any value sent by the
    client. `X-Forwarded-For` is ignored because clients can prepend arbitrary addresses to it. Without that header,
    the address of the TCP connection is used. Outside Fly.io, clients can set `Fly-Client-IP` themselves.
    """
    return request.headers.get("Fly-Client-IP") or (request.client.host if request.client else "unknown")


limiter = RateLimiter(settings.RATE_LIMITING_FREQUENCY, enabled=settings.RATE_LIMITING_ENABLE)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create the shared tfmkt client on startup and close it on shutdown."""
    app.state.tfmkt = TfmktClient()
    yield
    await app.state.tfmkt.aclose()


app = FastAPI(
    title="Transfermarkt API",
    version="4.2.0",
    description="Football data from Transfermarkt's JSON API: players, clubs and competitions.",
    lifespan=lifespan,
)
# health checks and the interactive docs (the root redirect, Swagger UI and the schema it loads) are not counted
RATE_LIMIT_EXEMPT_PATHS = {
    "/",
    "/health",
    *filter(None, (app.docs_url, app.swagger_ui_oauth2_redirect_url, app.redoc_url, app.openapi_url)),
}
app.include_router(api_router)


@app.middleware("http")
async def rate_limit(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Answer 429 when the client is over its budget. All API routes share one budget; see `RATE_LIMIT_EXEMPT_PATHS`."""
    if not limiter.enabled or request.url.path in RATE_LIMIT_EXEMPT_PATHS:
        return await call_next(request)
    key = client_ip(request)
    if not limiter.hit(key):
        return JSONResponse(
            {"error": f"Rate limit exceeded: {settings.RATE_LIMITING_FREQUENCY}"},
            status_code=429,
            headers={"Retry-After": str(limiter.retry_after(key))},
        )
    return await call_next(request)


@app.middleware("http")
async def track_upstream_fetches(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """
    Start a per-request record of upstream fetch times, used for `updatedAt`, and log the request.

    Replaces uvicorn's access log, which on Fly.io shows the proxy's address: this one shows `client_ip`.
    """
    track_fetches()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        target = f"{request.url.path}?{request.url.query}" if request.url.query else request.url.path
        access_log.info('%s - "%s %s" %d', client_ip(request), request.method, target, status)


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
