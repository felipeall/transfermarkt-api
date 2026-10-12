"""Public facade contracts, transport interception and offline replay."""

import asyncio
import json
from collections.abc import Awaitable
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

import httpx
import pytest
from pydantic import BaseModel

from examples.transports import RecordedResponse, RecordingTransport, ReplayTransport
from tests.cases import CASES
from tests.snapshots import SNAPSHOTS_DIR, normalize
from tests.upstream import FixtureStore
from transfermarkt_api import CacheConfig, EndpointUnavailable, NotFound, Transfermarkt, UpstreamError
from transfermarkt_api.schemas import ClubListing, Countries
from transfermarkt_api.tfmkt.freshness import data_fetched_at

pytestmark = pytest.mark.anyio
FETCHED_AT = datetime(2025, 1, 1, 12)


@pytest.fixture
def anyio_backend() -> str:
    """Use the SDK's asyncio runtime."""
    return "asyncio"


def call_route(tm: Transfermarkt, path: str) -> Awaitable[BaseModel]:
    """Map a recorded HTTP case to its public SDK method."""
    url = urlsplit(path)
    resource, entity, *operation = url.path.strip("/").split("/")
    if resource == "games":
        return tm.game(entity)
    name = f"search_{resource}" if entity == "search" else f"{resource.removesuffix('s')}_{operation[0]}"
    if resource == "coaches" and entity != "search":
        name = "coach_" + operation[0]
    args = {key: values[0] for key, values in parse_qs(url.query).items()}
    return getattr(tm, name)(unquote(operation[0] if entity == "search" else entity), **args)


def fixture_transport(store: FixtureStore, calls: list[str]) -> httpx.MockTransport:
    """Replay upstream responses with their original capture timestamp."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Record each URL before returning stored bytes."""
        calls.append(str(request.url))
        status, content_type, body = store.load(str(request.url))
        return httpx.Response(
            status,
            content=body,
            headers={"content-type": content_type},
            extensions={"transfermarkt_fetched_at": FETCHED_AT},
        )

    return httpx.MockTransport(handler)


@pytest.mark.parametrize("name,path", CASES, ids=[name for name, _ in CASES])
async def test_sdk_matches_http_snapshots(tfmkt_store: FixtureStore, name: str, path: str) -> None:
    """Each facade call reproduces the established HTTP model or error."""
    expected = json.loads((SNAPSHOTS_DIR / f"{name}.json").read_text())
    async with Transfermarkt(transport=fixture_transport(tfmkt_store, [])) as tm:
        if expected["status"] != 200:
            error_type = {404: NotFound, 501: EndpointUnavailable}[expected["status"]]
            with pytest.raises(error_type) as error:
                await call_route(tm, path)
            assert str(error.value) == expected["body"]["detail"]
        else:
            model = await call_route(tm, path)
            assert isinstance(model, BaseModel)
            assert model.updated_at == FETCHED_AT
            assert normalize(model.model_dump(mode="json", by_alias=True)) == expected["body"]


async def test_uncached_squad_replays_complete_request_graph(tfmkt_store: FixtureStore) -> None:
    """Every reference, batch and fan-out call is intercepted and replayable by URL."""
    calls: list[str] = []
    async with Transfermarkt(transport=fixture_transport(tfmkt_store, calls), cache=None) as tm:
        first = await tm.club_players("131")
        original_calls = calls.copy()
        calls.clear()
        second = await tm.club_players("131")
    assert first.model_dump() == second.model_dump()
    assert sorted(original_calls) == sorted(calls)
    paths = {urlsplit(url).path for url in calls}
    assert {"/attributes", "/club/131/squad", "/players", "/clubs"} <= paths
    assert any(path.startswith("/transfer/history/player/") for path in paths)


async def test_record_then_replay_exact_models(tfmkt_store: FixtureStore) -> None:
    """The documented adapters capture upstream bytes and replay full models, including fetch time."""
    records: dict[tuple[str, str], RecordedResponse] = {}
    recording = RecordingTransport(fixture_transport(tfmkt_store, []), records)
    async with Transfermarkt(transport=recording, cache=None) as tm:
        original = await tm.club_players("131", season_id="2014")
    assert records
    async with Transfermarkt(transport=ReplayTransport(records), cache=None) as tm:
        replayed = await tm.club_players("131", season_id="2014")
    assert original.model_dump(mode="json", by_alias=True) == replayed.model_dump(mode="json", by_alias=True)
    assert original.updated_at == min(record.fetched_at for record in records.values())


async def test_recording_preserves_failures_before_parsing() -> None:
    """Even malformed or blocked responses are recorded before SDK classification."""
    records: dict[tuple[str, str], RecordedResponse] = {}
    backend = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            content=b"blocked",
            headers={"x-amzn-waf-action": "challenge"},
        )
    )
    from transfermarkt_api import UpstreamBlocked

    async with Transfermarkt(transport=RecordingTransport(backend, records), cache=None) as tm:
        with pytest.raises(UpstreamBlocked):
            await tm.countries()
    record = records[("GET", "https://tmapi.transfermarkt.technology/attributes")]
    assert record.body == b"blocked"
    assert ("x-amzn-waf-action", "challenge") in record.headers


async def test_default_cache_and_client_isolation(tfmkt_store: FixtureStore) -> None:
    """Default caches reuse responses, but a second client fetches independently."""
    calls: list[str] = []
    async with Transfermarkt(transport=fixture_transport(tfmkt_store, calls)) as tm:
        first = await tm.club_players("131")
        count = len(calls)
        assert await tm.club_players("131") == first
        assert len(calls) == count
    async with Transfermarkt(transport=fixture_transport(tfmkt_store, calls)) as other:
        assert await other.club_players("131") == first
    assert len(calls) == 2 * count


async def test_transport_error_identity_and_sibling_cleanup() -> None:
    """Caller errors are untouched and fan-out work stops before the call returns."""
    sibling_started = asyncio.Event()
    sibling_stopped = asyncio.Event()
    failure = LookupError("no recording")

    async def handler(request: httpx.Request) -> httpx.Response:
        """Fail one squad branch while the reference branch remains blocked."""
        if request.url.path == "/attributes":
            sibling_started.set()
            try:
                await asyncio.Event().wait()
            finally:
                sibling_stopped.set()
        await sibling_started.wait()
        raise failure

    async with Transfermarkt(transport=httpx.MockTransport(handler), cache=None) as tm:
        with pytest.raises(LookupError) as error:
            await tm.club_players("1")
        assert error.value is failure
        assert sibling_stopped.is_set()


async def test_concurrency_cap_and_cancellation() -> None:
    """All fan-out uses the shared cap and cancellation drains active requests."""
    active = 0
    peak = 0
    started = asyncio.Event()

    async def handler(request: httpx.Request) -> httpx.Response:
        """Block until the caller cancels and measure concurrent upstream work."""
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            active -= 1
        raise AssertionError("unreachable")

    async with Transfermarkt(transport=httpx.MockTransport(handler), max_concurrency=1) as tm:
        task = asyncio.create_task(tm.club_players("1"))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert (active, peak) == (0, 1)


async def test_lifecycle_closes_transport_once() -> None:
    """Both exceptional context exit and repeated explicit close release resources once."""

    class Transport(httpx.AsyncBaseTransport):
        closed = 0

        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            """Provide empty country data."""
            return httpx.Response(200, json={"success": True, "data": {"countries": []}})

        async def aclose(self) -> None:
            """Count transport closure."""
            self.closed += 1

    transport = Transport()
    tm = Transfermarkt(transport=transport)
    with pytest.raises(RuntimeError, match="body failed"):
        async with tm:
            await tm.countries()
            raise RuntimeError("body failed")
    await tm.aclose()
    assert transport.closed == 1
    with pytest.raises(RuntimeError, match="closed"):
        await tm.countries()


async def test_concurrent_freshness_isolation() -> None:
    """Calls sharing one client do not mix their response timestamps or leak to the caller."""
    times = {"1": datetime(2020, 1, 1), "2": datetime(2021, 1, 1)}

    async def handler(request: httpx.Request) -> httpx.Response:
        """Force calls sharing the client to overlap with different capture times."""
        await asyncio.sleep(0)
        if request.url.path == "/competitions":
            entity_id = request.url.params.get_list("ids[]")[0]
            data: Any = [{"id": entity_id, "name": "Test"}]
        else:
            entity_id = request.url.path.split("/")[2]
            data = {"seasons": []}
        return httpx.Response(
            200, json={"success": True, "data": data}, extensions={"transfermarkt_fetched_at": times[entity_id]}
        )

    async with Transfermarkt(transport=httpx.MockTransport(handler), cache=None) as tm:
        first, second = await asyncio.gather(tm.competition_seasons("1"), tm.competition_seasons("2"))
        assert (first.updated_at, second.updated_at) == (times["1"], times["2"])
    assert data_fetched_at() > datetime(2021, 1, 1)


async def test_invalid_model_becomes_upstream_error() -> None:
    """Model validation failures expose SDK errors with the Pydantic cause."""
    async with Transfermarkt(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"success": True, "data": {"countries": [{"id": "bad"}]}}),
        )
    ) as tm:
        with pytest.raises(UpstreamError) as error:
            await tm.countries()
    assert error.value.__cause__ is not None


@pytest.mark.parametrize("kwargs", [{"max_concurrency": 0}, {"max_concurrency": True}, {"base_url": "relative"}])
async def test_invalid_constructor_arguments(kwargs: dict) -> None:
    """Invalid configuration is rejected before any I/O."""
    with pytest.raises(ValueError):
        Transfermarkt(**kwargs)


async def test_country_listing_and_argument_validation() -> None:
    """Country endpoints return typed models and invalid arguments never reach the transport."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Serve a minimal country directory."""
        data = {
            "/attributes": {"countries": [{"id": 9, "name": "Test", "isHistorical": False}]},
            "/country/9/club": {"clubIds": []},
        }[request.url.path]
        return httpx.Response(200, json={"success": True, "data": data})

    async with Transfermarkt(transport=httpx.MockTransport(handler)) as tm:
        assert isinstance(await tm.countries(), Countries)
        assert isinstance(await tm.clubs(9), ClubListing)
        for method, args in (
            (tm.clubs, {"country_id": 0}),
            (tm.search_players, {"player_name": "x", "page_number": 0}),
        ):
            with pytest.raises(ValueError):
                await method(**args)
    with pytest.raises(ValueError):
        CacheConfig(ttl=0)
