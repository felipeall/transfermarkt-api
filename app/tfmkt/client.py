"""Async client for Transfermarkt's JSON API (tfmkt), the data source of every endpoint migrated off HTML scraping."""

import asyncio
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Optional

import httpx
from cachetools import TTLCache
from fastapi import HTTPException

from app.settings import settings
from app.tfmkt.freshness import record_fetch

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
            fetched_at, data = cache[key]
            record_fetch(fetched_at)
            return data

        async with self.semaphore:
            try:
                response = await self.http.send(request)
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail=f"Upstream timeout for {path}")
            except httpx.HTTPError as e:
                raise HTTPException(status_code=502, detail=f"Upstream connection error for {path}: {e}")

        data = self._parse(response, path)
        fetched_at = datetime.now()
        cache[key] = (fetched_at, data)
        record_fetch(fetched_at)
        return data

    async def get_optional(self, path: str, params: Optional[list[tuple[str, Any]]] = None) -> Any:
        """Like `get`, but returns None when upstream answers 404 (e.g. a club without a stadium)."""
        try:
            return await self.get(path, params=params)
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise

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

    async def quick_search(self, term: str, page: int) -> dict:
        """Search players, clubs, competitions and coaches; returns IDs per category."""
        return await self.get("/quick-search", params=[("term", term), ("page", page)])

    async def player(self, player_id: str) -> dict:
        """Fetch a player record."""
        return await self.get(f"/player/{player_id}")

    async def player_market_value_history(self, player_id: str) -> dict:
        """Fetch a player's market value history and current value."""
        return await self.get(f"/player/{player_id}/market-value-history")

    async def player_transfer_history(self, player_id: str) -> Optional[dict]:
        """None when the player has no transfer history (upstream answers 404)."""
        return await self.get_optional(f"/transfer/history/player/{player_id}")

    async def player_injuries(self, player_id: str) -> dict:
        """Fetch a player's injury history."""
        return await self.get(f"/player/{player_id}/injury")

    async def player_performance_games(self, player_id: str) -> dict:
        """Fetch one performance record per match of the player's club."""
        return await self.get(f"/player/{player_id}/performance-game")

    async def player_achievements(self, player_id: str) -> dict:
        """Fetch a player's titles and awards (one record per title won)."""
        return await self.get(f"/player/{player_id}/achievement")

    async def player_market_value_ranking(self, player_id: str) -> Optional[dict]:
        """None when the player has no ranking (upstream answers 404)."""
        return await self.get_optional(f"/player/{player_id}/market-value-ranking")

    async def player_national_career(self, player_id: str) -> dict:
        """Fetch the national teams a player has played for."""
        return await self.get(f"/player/{player_id}/national-career-history")

    async def player_absences(self, player_id: str) -> dict:
        """Fetch a player's non-injury absences."""
        return await self.get(f"/player/{player_id}/absence")

    async def coach(self, coach_id: str) -> dict:
        """Fetch a coach record."""
        return await self.get(f"/coach/{coach_id}")

    async def coaches(self, ids: Iterable[str]) -> dict[str, dict]:
        """Fetch coach records by ID, indexed by ID."""
        return await self.get_batch("/coaches", ids)

    async def country_clubs(self, country_id: int) -> dict:
        """Fetch the limited club directory for a country; no upstream pagination is available."""
        return await self.get(f"/country/{country_id}/club")

    async def club(self, club_id: str) -> dict:
        """Fetch a club record."""
        return await self.get(f"/club/{club_id}")

    async def club_squad(self, club_id: str, season_id: Optional[str] = None) -> dict:
        """Fetch a club's squad for a season (current squad by default)."""
        return await self.get(f"/club/{club_id}/squad", params=_season(season_id))

    async def club_achievements(self, club_id: str) -> dict:
        """Fetch a club's titles (one record per title won)."""
        return await self.get(f"/club/{club_id}/achievement")

    async def club_coach(self, club_id: str) -> Optional[dict]:
        """None when the club has no head coach on record (upstream answers 404)."""
        return await self.get_optional(f"/club/{club_id}/coach")

    async def club_stadium(self, club_id: str) -> Optional[dict]:
        """None when the club has no stadium (upstream answers 404)."""
        return await self.get_optional(f"/club/{club_id}/stadium")

    async def competition_clubs(self, competition_id: str, season_id: Optional[str] = None) -> dict:
        """Fetch the member clubs of a competition season (current by default)."""
        return await self.get(f"/competition/{competition_id}/club", params=_season(season_id))

    async def competition_table(self, competition_id: str, season_id: Optional[str] = None) -> dict:
        """Fetch a competition's league table(s) for a season (current by default)."""
        return await self.get(f"/competition/{competition_id}/table", params=_season(season_id))

    async def competition_seasons(self, competition_id: str) -> dict:
        """Fetch the seasons available for a competition."""
        return await self.get(f"/competition/{competition_id}/season")

    async def game(self, game_id: str) -> dict:
        """Fetch a match: lineups, events, score and officials."""
        return await self.get(f"/game/{game_id}")

    async def stadium(self, stadium_id: str) -> Optional[dict]:
        """None when the stadium is unknown (upstream answers 404)."""
        return await self.get_optional(f"/stadium/{stadium_id}")

    async def competitions(self, ids: Iterable[str]) -> dict[str, dict]:
        """Fetch competition records by ID, indexed by ID."""
        return await self.get_batch("/competitions", ids)

    async def clubs(self, ids: Iterable[str]) -> dict[str, dict]:
        """Fetch club records by ID, indexed by ID."""
        return await self.get_batch("/clubs", ids)

    async def players(self, ids: Iterable[str]) -> dict[str, dict]:
        """Fetch player records by ID, indexed by ID."""
        return await self.get_batch("/players", ids)


def _season(season_id: Optional[str]) -> Optional[list[tuple[str, str]]]:
    """Query parameters selecting a season, or None for the current season."""
    return [("season", season_id)] if season_id else None
