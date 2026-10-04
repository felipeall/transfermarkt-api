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
def limited_client() -> Iterator[TestClient]:
    """API client with rate limiting enabled and empty counters."""
    enabled = limiter.enabled
    limiter.enabled = True
    limiter.reset()
    with TestClient(app) as client:
        yield client
    limiter.enabled = enabled
    limiter.reset()


def test_requests_over_the_limit_get_429(limited_client: TestClient) -> None:
    """The default limit (2 per 3 seconds) answers 429 to the third request from the same client."""
    statuses = [limited_client.get("/", follow_redirects=False).status_code for _ in range(3)]

    assert statuses == [307, 307, 429]


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
