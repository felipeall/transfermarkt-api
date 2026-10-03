import json
from collections.abc import Callable
from typing import NoReturn

import httpx
import pytest
from fastapi import HTTPException

from app.tfmkt.client import BATCH_SIZE, TfmktClient
from tests.upstream import FixtureStore

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Run async tests on asyncio."""
    return "asyncio"


def ok(data: object) -> httpx.Response:
    """A successful tfmkt response wrapping `data`."""
    return httpx.Response(200, json={"success": True, "message": "OK", "data": data})


def client_for(handler: Callable[[httpx.Request], httpx.Response]) -> TfmktClient:
    """A client whose requests are answered by `handler`."""
    return TfmktClient(base_url="https://tfmkt.test", transport=httpx.MockTransport(handler))


async def test_returns_data_payload() -> None:
    """Successful responses return the `data` payload."""
    tfmkt = client_for(lambda request: ok({"id": "28003"}))

    assert await tfmkt.get("/player/28003") == {"id": "28003"}


@pytest.mark.parametrize(
    "response,status",
    [
        (httpx.Response(404, json={"success": False, "message": "Player not found"}), 404),
        (httpx.Response(202, content=b"", headers={"x-amzn-waf-action": "challenge"}), 503),
        (httpx.Response(202, content=b""), 503),
        (httpx.Response(403, content=b"Forbidden"), 503),
        (httpx.Response(429, content=b"Too Many Requests"), 503),
        (httpx.Response(500, content=b"oops"), 502),
        (httpx.Response(200, content=b"<html>not json</html>"), 502),
        (httpx.Response(200, json={"success": False, "message": "error"}), 502),
    ],
)
async def test_maps_upstream_failures(response: httpx.Response, status: int) -> None:
    """Upstream failures map to the documented HTTP errors."""
    tfmkt = client_for(lambda request: response)

    with pytest.raises(HTTPException) as error:
        await tfmkt.get("/player/28003")

    assert error.value.status_code == status


async def test_timeout_maps_to_504() -> None:
    """Upstream timeouts become 504."""

    def handler(request: httpx.Request) -> NoReturn:
        """Simulate a read timeout."""
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(HTTPException) as error:
        await client_for(handler).get("/player/28003")

    assert error.value.status_code == 504


async def test_caches_successful_responses() -> None:
    """A repeated request is served from the cache."""
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        """Count requests and answer successfully."""
        calls.append(request.url)
        return ok({"id": "28003"})

    tfmkt = client_for(handler)
    await tfmkt.get("/player/28003")
    await tfmkt.get("/player/28003")

    assert len(calls) == 1


async def test_does_not_cache_failures() -> None:
    """Failed responses are not cached."""
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        """Count requests and answer with a server error."""
        calls.append(request.url)
        return httpx.Response(500)

    tfmkt = client_for(handler)
    for _ in range(2):
        with pytest.raises(HTTPException):
            await tfmkt.get("/player/28003")

    assert len(calls) == 2


async def test_batch_chunks_ids_and_indexes_by_id() -> None:
    """Batch lookups are chunked and indexed by ID; unknown IDs are absent."""
    requested = []

    def handler(request: httpx.Request) -> httpx.Response:
        """Answer with the requested IDs except 7, in reverse order."""
        ids = request.url.params.get_list("ids[]")
        requested.append(ids)
        # upstream may omit unknown IDs and returns entities in its own order
        return ok([{"id": i} for i in reversed(ids) if i != "7"])

    ids = [str(i) for i in range(BATCH_SIZE + 5)] + ["3", None, ""]
    result = await client_for(handler).get_batch("/players", ids)

    assert [len(chunk) for chunk in requested] == [BATCH_SIZE, 5]
    assert set(result) == {str(i) for i in range(BATCH_SIZE + 5)} - {"7"}
    assert result["3"] == {"id": "3"}


async def test_batch_with_no_ids_makes_no_request() -> None:
    """A batch lookup without IDs makes no request."""

    def handler(request: httpx.Request) -> NoReturn:
        """Fail if any request is made."""
        raise AssertionError(f"unexpected request {request.url}")

    assert await client_for(handler).get_batch("/players", [None, ""]) == {}


def test_recorded_fixture_is_valid_json(tfmkt_store: FixtureStore) -> None:
    """Recorded fixtures are valid tfmkt payloads, successful exactly when the status is 200."""
    for url in tfmkt_store.manifest:
        status, _, content = tfmkt_store.load(url)
        assert json.loads(content)["success"] is (status == 200), url
