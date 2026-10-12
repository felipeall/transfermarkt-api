# 1. Expose a Python SDK alongside the HTTP service

Status: Proposed — 2026-10-12

Implementation plan: [Python SDK](../plans/0001-python-sdk.md).

## Context

transfermarkt-api runs only as a FastAPI service. A consumer has to run the service and call it over HTTP, even when
the consumer is itself a Python program that could call the same code in-process.

Calling the service also hides the upstream traffic. One `/clubs/{id}/players` call fans out to `/club/{id}/squad`,
`/attributes`, batched `/players` and `/clubs`, and one `/transfer/history/player/{id}` per player. A consumer that
wants to rate-limit, proxy, record or replay requests to `tmapi.transfermarkt.technology` cannot, because it only
sees the service's assembled output.

Most of what an SDK needs already exists. `TfmktClient` accepts an `httpx.AsyncBaseTransport`. Services are plain
async functions that take the client. Response shapes are Pydantic models in `app/schemas/`. The remaining coupling
is to FastAPI (`HTTPException` raised from the client and services), to environment settings read at import time,
and to the package layout (`app`, `package = false`).

## Decision

Publish the services and schemas as an importable async library. The FastAPI app becomes one consumer of it.

1. **Installable package.** The core install pulls only `httpx`, `pydantic` and what the services need. FastAPI,
   uvicorn, `limits` and `pydantic-settings` move to a `server` extra. The import name is not `app`; for example
   `transfermarkt_api`. Library dependencies are declared as compatible ranges (`pydantic>=2.13,<3`), not exact pins,
   so the package installs next to an application's own lockfile; `uv.lock` keeps pinning the server. The package
   ships a `py.typed` marker so type checkers use its annotations.
2. **Public facade.** One async client object with a method per endpoint, mirroring the HTTP routes and returning the
   existing response models (`ClubPlayers`, `CompetitionClubs`, …). It works as an async context manager.
3. **Bring your own transport.** The facade accepts an `httpx.AsyncBaseTransport`. Every upstream request goes
   through it: reference data, batch routes and fan-out calls included. That transport is where the caller applies
   rate limits, retries, proxies or response recording.
4. **Caching is optional.** The in-memory TTL caches stay on by default and turn off with `cache=None`, so every
   upstream request reaches the transport. `CacheConfig` configures ordinary/reference TTLs and cache capacity.
5. **Library exceptions, not `HTTPException`.** The client and services raise SDK exceptions: `NotFound`,
   `UpstreamBlocked` (WAF challenge, 403, 429), `UpstreamTimeout` and `UpstreamError`. The server maps them to
   404, 503, 504 and 502 as today. The default transport's `httpx` timeouts and connection errors map to SDK exceptions.
   Exceptions from an injected transport propagate unchanged, including native `httpx` exceptions and caller-defined
   errors. Callers supplying a transport classify `httpx.TimeoutException` / `httpx.TransportError` themselves.
   `EndpointUnavailable` covers routes without an upstream data source and maps to the existing server `501`.
6. **Configuration by argument.** Base URL, timeout and concurrency cap are constructor arguments with today's
   defaults. Importing the library reads no `.env` and no environment variables.
7. **Replayable assembly.** Given the same upstream responses, a service produces the same output. Requests are built
   deterministically (batch IDs already sorted), so a caller can re-run assembly by serving stored responses keyed by
   request method and full URL. Replay transports can set `httpx.Response.extensions["transfermarkt_fetched_at"]`
   to the original capture datetime. Aware timestamps are normalized to UTC; naive timestamps are interpreted as UTC.
   `updatedAt` retains the existing naive JSON representation and represents UTC. Without metadata, it reflects the
   current UTC fetch time.
8. **Versioning.** The facade, response models, exceptions and cache configuration are the public API, under semantic
   versioning. A breaking change to any of them is a major release.

### Basic usage

A standalone script with the default transport, defaults for every setting, and the built-in cache:

```python
import asyncio

from transfermarkt_api import Transfermarkt


async def main() -> None:
    async with Transfermarkt() as tm:
        squad = await tm.club_players("985")  # current squad
        for player in squad.players:
            print(player.shirt_number, player.name, player.position, player.market_value)


asyncio.run(main())
```

## Consequences

- Python consumers use the library in-process: no service to run, and full control over every upstream request.
- The server keeps its behaviour, its rate limiting and its caches; it moves on top of the library.
- The facade, schemas, exceptions and cache configuration become a public API. Breaking changes need a major release, and the
  CHANGELOG has to call out changes to response models.
- Service modules and the low-level upstream client are implementation details.
- Moving out of the `app` package and replacing `HTTPException` in services touches most modules in one change.
- A parser fix reaches consumers as a release; callers that stored upstream responses can re-run assembly instead of
  re-fetching.
