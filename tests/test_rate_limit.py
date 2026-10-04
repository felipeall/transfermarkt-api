"""Rate limiting: per-client keys that callers cannot spoof, and a health check that is never limited."""

import logging
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.main import app, client_ip, limiter


def request_with(headers: dict[str, str], client: tuple[str, int] = ("10.0.0.1", 1234)) -> Request:
    """A bare request from `client` carrying `headers`."""
    raw = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    return Request({"type": "http", "method": "GET", "path": "/", "headers": raw, "client": client})


def test_client_ip_prefers_fly_client_ip() -> None:
    """On Fly.io, the address the proxy accepted the connection from is the key."""
    assert client_ip(request_with({"Fly-Client-IP": "203.0.113.7"})) == "203.0.113.7"


def test_client_ip_ignores_x_forwarded_for() -> None:
    """A spoofed X-Forwarded-For does not change the key."""
    assert client_ip(request_with({"X-Forwarded-For": "198.51.100.1"})) == "10.0.0.1"


@pytest.fixture
def limited_client(client: TestClient) -> Iterator[TestClient]:
    """API client served from recorded fixtures, with rate limiting enabled and empty counters."""
    enabled = limiter.enabled
    limiter.enabled = True
    limiter.reset()
    yield client
    limiter.enabled = enabled
    limiter.reset()


def test_requests_over_the_limit_get_429(limited_client: TestClient) -> None:
    """The default limit (2 per 3 seconds) answers 429 to the third request from the same client."""
    statuses = [limited_client.get("/", follow_redirects=False).status_code for _ in range(3)]

    assert statuses == [307, 307, 429]


def test_limit_is_shared_across_urls(limited_client: TestClient) -> None:
    """Requests to different URLs count against one budget, so walking through IDs is limited too."""
    statuses = [
        limited_client.get(path, follow_redirects=False).status_code for path in ("/", "/docs", "/openapi.json")
    ]

    assert statuses == [307, 200, 429]


def test_api_routes_are_limited(limited_client: TestClient) -> None:
    """Routes from the API routers count too, with a Retry-After header on the 429."""
    paths = ["/players/28003/market_value", "/players/17259/market_value", "/players/28003/profile"]
    responses = [limited_client.get(path) for path in paths]

    assert [r.status_code for r in responses] == [200, 200, 429]
    assert int(responses[-1].headers["Retry-After"]) >= 1


def test_clients_have_separate_budgets(limited_client: TestClient) -> None:
    """One client over its limit does not block another."""
    for _ in range(3):
        limited_client.get("/", headers={"Fly-Client-IP": "203.0.113.7"}, follow_redirects=False)

    other = limited_client.get("/", headers={"Fly-Client-IP": "203.0.113.8"}, follow_redirects=False)

    assert other.status_code == 307


def test_spoofed_x_forwarded_for_shares_the_limit(limited_client: TestClient) -> None:
    """Changing X-Forwarded-For on each request does not reset the limit."""
    statuses = [
        limited_client.get("/", headers={"X-Forwarded-For": f"198.51.100.{i}"}, follow_redirects=False).status_code
        for i in range(3)
    ]

    assert statuses[-1] == 429


def test_health_is_not_limited(limited_client: TestClient) -> None:
    """Platform health checks are never rate limited."""
    assert {limited_client.get("/health").status_code for _ in range(5)} == {200}


def test_access_log_shows_client_ip(caplog: pytest.LogCaptureFixture) -> None:
    """Each request is logged with the client IP from `Fly-Client-IP`, not the proxy's address."""
    with TestClient(app) as client, caplog.at_level(logging.INFO, logger="uvicorn.error"):
        client.get("/health?probe=1", headers={"Fly-Client-IP": "203.0.113.7"})

    assert '203.0.113.7 - "GET /health?probe=1" 200' in caplog.messages


def test_access_log_includes_429(limited_client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    """Requests refused with 429 are logged too."""
    with caplog.at_level(logging.INFO, logger="uvicorn.error"):
        for _ in range(3):
            limited_client.get("/", headers={"Fly-Client-IP": "203.0.113.7"}, follow_redirects=False)

    assert '203.0.113.7 - "GET /" 429' in caplog.messages
