"""Minimal recording/replay adapters; real consumers provide their own durable store."""

from dataclasses import dataclass
from datetime import datetime

import httpx


@dataclass(frozen=True)
class RecordedResponse:
    """Decoded upstream response saved before the SDK sees or parses it."""

    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes
    fetched_at: datetime


class RecordingTransport(httpx.AsyncBaseTransport):
    """Wrap a caller-selected backend and capture responses before SDK parsing."""

    def __init__(
        self,
        backend: httpx.AsyncBaseTransport,
        records: dict[tuple[str, str], RecordedResponse],
    ) -> None:
        """Use a backend and an example in-memory store keyed by method and full URL."""
        self.backend = backend
        self.records = records

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Save successful and failed responses, preserving headers used for WAF classification."""
        response = await self.backend.handle_async_request(request)
        try:
            body = await response.aread()
        finally:
            await response.aclose()
        # aread decodes compressed content. Reconstructed responses must not decode it twice.
        headers = tuple(
            (key, value)
            for key, value in response.headers.multi_items()
            if key.lower() not in ("content-encoding", "content-length")
        )
        record = RecordedResponse(response.status_code, headers, body, datetime.now())
        self.records[(request.method, str(request.url))] = record
        return httpx.Response(
            record.status,
            headers=record.headers,
            content=record.body,
            extensions={"transfermarkt_fetched_at": record.fetched_at},
        )

    async def aclose(self) -> None:
        """Close the owned backend when the SDK closes its transport."""
        await self.backend.aclose()


class ReplayTransport(httpx.AsyncBaseTransport):
    """Serve stored responses only; missing recordings never fall back to network access."""

    def __init__(self, records: dict[tuple[str, str], RecordedResponse]) -> None:
        """Use previously recorded upstream responses."""
        self.records = records

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Recreate the original response and its fetch timestamp, or raise KeyError."""
        record = self.records[(request.method, str(request.url))]
        return httpx.Response(
            record.status,
            headers=record.headers,
            content=record.body,
            extensions={"transfermarkt_fetched_at": record.fetched_at},
        )
