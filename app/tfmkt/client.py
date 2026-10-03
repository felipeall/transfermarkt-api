"""Async client for Transfermarkt's JSON API (tfmkt), the data source of every endpoint migrated off HTML scraping."""

import asyncio
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Optional

import httpx
from cachetools import TTLCache
from fastapi import HTTPException

from app.settings import settings

BATCH_SIZE = 100  # batch routes accepted 200 IDs in testing; stay well below


class TfmktClient:
    """
    Thin wrapper around tfmkt routes.

    Every request goes through `get`, which applies the concurrency cap, the response cache and the upstream error
    mapping. Successful responses are cached with the time they were fetched, so callers can report data age.
    """

    def __init__(
        self,
        base_url: str = settings.TFMKT_BASE_URL,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        """Create the HTTP client, concurrency cap and response caches."""
        self.http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Accept": "application/json", "User-Agent": "transfermarkt-api"},
            timeout=settings.TFMKT_TIMEOUT_SECONDS,
            transport=transport,
        )
        self.semaphore = asyncio.Semaphore(settings.TFMKT_MAX_CONCURRENCY)
        self.cache: TTLCache = TTLCache(maxsize=settings.CACHE_MAX_ENTRIES, ttl=settings.CACHE_TTL_SECONDS)
        self.reference_cache: TTLCache = TTLCache(maxsize=8, ttl=settings.CACHE_REFERENCE_TTL_SECONDS)

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self.http.aclose()

    async def get(self, path: str, params: Optional[list[tuple[str, Any]]] = None, reference: bool = False) -> Any:
        """
        Fetch a tfmkt route and return its `data` payload.

        Raises:
            HTTPException: 404 when upstream does not know the entity, 503 when upstream challenges or rejects the
                request, 504 on timeout and 502 for any other unexpected upstream response.
        """
        request = self.http.build_request("GET", path, params=params)
        key = str(request.url)
        cache = self.reference_cache if reference else self.cache
        if key in cache:
            return cache[key][1]

        async with self.semaphore:
            try:
                response = await self.http.send(request)
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail=f"Upstream timeout for {path}")
            except httpx.HTTPError as e:
                raise HTTPException(status_code=502, detail=f"Upstream connection error for {path}: {e}")

        data = self._parse(response, path)
        cache[key] = (datetime.now(), data)
        return data

    @staticmethod
    def _parse(response: httpx.Response, path: str) -> Any:
        """Return the `data` payload of a tfmkt response, or raise the HTTPException matching the failure."""
        if response.headers.get("x-amzn-waf-action") or (response.status_code == 202 and not response.content):
            raise HTTPException(status_code=503, detail=f"Upstream blocked the request (WAF challenge) for {path}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Not found: {path}")
        if response.status_code in (403, 429):
            raise HTTPException(status_code=503, detail=f"Upstream refused the request ({response.status_code})")
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Unexpected upstream status {response.status_code}")
        try:
            body = response.json()
        except ValueError:
            raise HTTPException(status_code=502, detail=f"Upstream returned invalid JSON for {path}")
        if not isinstance(body, dict) or not body.get("success") or "data" not in body:
            raise HTTPException(status_code=502, detail=f"Unexpected upstream payload for {path}")
        return body["data"]

    async def get_batch(self, route: str, ids: Iterable[str]) -> dict[str, dict]:
        """
        Fetch entities from a batch route (`/players`, `/clubs`, `/competitions`) and index them by ID.

        IDs that upstream does not return are simply absent from the result; callers must handle the gap.
        """
        unique_ids = sorted({str(i) for i in ids if i not in (None, "")})
        chunks = [unique_ids[i : i + BATCH_SIZE] for i in range(0, len(unique_ids), BATCH_SIZE)]
        results = await asyncio.gather(*(self.get(route, params=[("ids[]", i) for i in chunk]) for chunk in chunks))
        return {str(entity["id"]): entity for data in results for entity in data or []}

    async def attributes(self) -> dict:
        """Reference data: countries, positions, competition types, confederations, injuries, etc."""
        return await self.get("/attributes", reference=True)

    async def player_performance_games(self, player_id: str) -> dict:
        """Fetch one performance record per match of the player's club."""
        return await self.get(f"/player/{player_id}/performance-game")

    async def competitions(self, ids: Iterable[str]) -> dict[str, dict]:
        """Fetch competition records by ID, indexed by ID."""
        return await self.get_batch("/competitions", ids)

    async def clubs(self, ids: Iterable[str]) -> dict[str, dict]:
        """Fetch club records by ID, indexed by ID."""
        return await self.get_batch("/clubs", ids)

    async def players(self, ids: Iterable[str]) -> dict[str, dict]:
        """Fetch player records by ID, indexed by ID."""
        return await self.get_batch("/players", ids)
