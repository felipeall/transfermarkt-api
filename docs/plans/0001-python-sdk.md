# Python SDK implementation plan

Implements [ADR 0001](../adr/0001-python-sdk.md). The implementation accompanies this plan; the ADR remains
proposed until review. The steps below describe the implementation boundaries and verification gates.

## Outcome and scope

Ship an installable async `transfermarkt_api` library that assembles the existing response models in-process.
Keep the HTTP service working with its current routes, response bodies, error statuses, environment configuration,
rate limiting and cache defaults. A Python caller must be able to intercept every upstream request, persist its
response before parsing, and replay assembly without network access.

Reuse the existing services and recorded fixtures. Do not add ingestion orchestration, persistence, automatic
pagination, a synchronous client, SDK retries, circuit breakers or source-specific proxy integrations. Those policies
belong to the caller's transport. Keep the existing Python `>=3.12,<3.14` support range for this change.

## Public contract

Use `from transfermarkt_api import Transfermarkt`, with models under `transfermarkt_api.schemas` and exceptions
under `transfermarkt_api.exceptions`, also re-exported from the package root. Preserve model names, field types,
nullability and camel-case JSON aliases. Methods return validated Pydantic models, not the dictionaries currently
returned by services. `model_dump(mode="json", by_alias=True)` produces the HTTP representation.

Proposed constructor contract:

```python
Transfermarkt(
    *,
    base_url="https://tmapi.transfermarkt.technology",
    timeout=15.0,
    max_concurrency=10,
    transport=None,
    cache=CacheConfig(),
)
```

`CacheConfig` is an immutable configuration object with response TTL `600`, reference TTL `86400`, and response
capacity `2000`; retain the reference-cache capacity of `8`. `cache=None` disables both caches, including
`/attributes`. Allocate cache instances per client, never in a default argument. Export `CacheConfig` publicly.
Validate positive concurrency and cache capacity, valid TTLs and the base URL before doing I/O; use `ValueError`
for invalid SDK arguments. Accept the timeout forms supported by `httpx`, including `httpx.Timeout`.

Each instance owns its HTTP client, semaphore, caches and supplied transport. `async with` and explicit `aclose()`
close these resources; closing twice is harmless. Document that a supplied transport is closed with the SDK, and
must not be shared across clients without a caller-owned wrapper controlling closure. Create no requests on import
or construction. Support concurrent methods on one client within one event loop, not cross-loop use.

| HTTP route | SDK method → model |
| --- | --- |
| `/countries/` | `countries()` → `Countries` |
| `/clubs/?country_id=` | `clubs(country_id)` → `ClubListing` |
| `/clubs/search/{club_name}` | `search_clubs(club_name, *, page_number=1)` → `ClubSearch` |
| `/clubs/{club_id}/profile` | `club_profile(club_id)` → `ClubProfile` |
| `/clubs/{club_id}/players` | `club_players(club_id, *, season_id=None)` → `ClubPlayers` |
| `/clubs/{club_id}/achievements` | `club_achievements(club_id)` → `Achievements` |
| `/players/search/{player_name}` | `search_players(player_name, *, page_number=1)` → `PlayerSearch` |
| `/players/{player_id}/profile` | `player_profile(player_id)` → `PlayerProfile` |
| `/players/{player_id}/market_value` | `player_market_value(player_id)` → `PlayerMarketValue` |
| `/players/{player_id}/transfers` | `player_transfers(player_id)` → `PlayerTransfers` |
| `/players/{player_id}/stats` | `player_stats(player_id)` → `PlayerStats` |
| `/players/{player_id}/matches` | `player_matches(player_id, *, season_id=None, page_number=1)` → `PlayerMatches` |
| `/players/{player_id}/injuries` | `player_injuries(player_id, *, page_number=1)` → `PlayerInjuries` |
| `/players/{player_id}/absences` | `player_absences(player_id, *, page_number=1)` → `PlayerAbsences` |
| `/players/{player_id}/achievements` | `player_achievements(player_id)` → `Achievements` |
| `/players/{player_id}/national_career` | `player_national_career(player_id)` → `PlayerNationalCareer` |
| `/players/{player_id}/jersey_numbers` | `player_jersey_numbers(player_id)` → raises `EndpointUnavailable` |
| `/coaches/search/{coach_name}` | `search_coaches(coach_name, *, page_number=1)` → `CoachSearch` |
| `/coaches/{coach_id}/profile` | `coach_profile(coach_id)` → `CoachProfile` |
| `/competitions/search/{competition_name}` | `search_competitions(competition_name, *, page_number=1)` → `CompetitionSearch` |
| `/competitions/{competition_id}/clubs` | `competition_clubs(competition_id, *, season_id=None)` → `CompetitionClubs` |
| `/competitions/{competition_id}/table` | `competition_table(competition_id, *, season_id=None)` → `CompetitionTable` |
| `/competitions/{competition_id}/seasons` | `competition_seasons(competition_id)` → `CompetitionSeasons` |
| `/games/{game_id}` | `game(game_id)` → `Game` |

Use string entity and season IDs, integer country IDs, and 1-based page numbers. Reject pages below `1` and country
IDs below `1` locally. Preserve single-page behavior, search ranking, upstream squad order, missing batch members,
and historical-season semantics. Health and documentation routes are server-only.

The ADR records two additional details: `EndpointUnavailable` preserves the existing unsupported endpoint, and
replay timestamps have an explicit transport metadata contract. The facade, schemas, exceptions and configuration
types are supported public API; service modules and the low-level upstream client remain implementation details.

## Implementation sequence

### 1. Extract a framework-independent core

- Create `transfermarkt_api/` at repository root. Move `app/tfmkt`, `app/services` and `app/schemas` into it and update
  imports. Keep `app/` as the server adapter, preserving `uvicorn app.main:app`.
- Keep package initialization lightweight. Move `get_tfmkt` and the FastAPI `Tfmkt` dependency alias from
  `app/tfmkt/__init__.py` into a server dependency module, such as `app/api/dependencies.py`.
- Replace the low-level client's `settings` imports and bound defaults with literal defaults and explicit
  constructor parameters. Only the server imports `app.settings` and translates environment values into arguments.
- Extract countries validation and assembly from `app/api/endpoints/countries.py` into a core service so both
  entry points use the same behavior.
- Add `TransfermarktError`, `NotFound`, `UpstreamBlocked`, `UpstreamTimeout`, `UpstreamError` and
  `EndpointUnavailable`. Preserve current messages. Include optional upstream URL and status metadata where
  available, without importing HTTP server types. Chain the original `httpx` exception as the cause.
- Replace `HTTPException` in the client, optional-fetch logic, competition services and club listing. Catch only
  `NotFound` for optional resources. Map timeout before the broader `httpx.HTTPError`; leave custom transport
  exceptions and cancellation untouched. Do not catch arbitrary `Exception` around assembly.
- In the server, register explicit mappings to `404`, `503`, `504`, `502` and `501`, retaining `{"detail": ...}`.
  Preserve the existing WAF-header, empty `202`, `403`, `429`, malformed JSON and invalid envelope behavior.

**Gate:** existing offline endpoint snapshots, regressions and rate-limit tests pass after import updates;
the core contains no FastAPI, settings, uvicorn or rate-limiter imports.

### 2. Add transport, cache and lifecycle controls

- Thread constructor settings and the supplied transport into the one underlying `httpx.AsyncClient`. Keep every
  reference lookup, batch and per-player fan-out on the same request path. Retain the default headers and sorted,
  deduplicated batch IDs with chunks of `100`.
- Implement `CacheConfig` and bypass all cache reads and writes when disabled. Store successful payloads with their
  fetch timestamps; errors never enter either cache. Keep cache state isolated by instance and upstream base URL.
- Retain one semaphore per client for all outgoing requests, and one shared client across all server requests.
  Concurrency caps in-flight calls; it is not a requests-per-second budget. Keep SDK retries absent so caller
  policies observe every attempt.
- Implement context management and deterministic cleanup, including error exits. Ensure fan-out tasks do not
  continue using a closed transport when one request fails or the caller cancels; cancel and await sibling tasks
  before returning the failure, while preserving successful output ordering.

**Gate:** spy transports see the complete squad request graph; repeated uncached calls include reference requests;
defaults still cache; concurrency bounds, instance isolation and transport closure are verified offline.

### 3. Build the typed facade and request-scoped freshness

- Implement the method table as thin service calls followed by `model_validate`. Avoid duplicating parsing logic.
  Convert response-model `ValidationError` into `UpstreamError` with its cause, inside the validation step only.
- Replace `track_fetches()` with a token-based context manager that creates a fresh list per facade call and resets
  it in `finally`. Child tasks may share that call's list; independent concurrent calls must not share it.
- Validate the final model before leaving that scope, so `AuditMixin.updated_at` uses the oldest response actually
  used in that call, including cache hits. Do not depend on HTTP middleware to establish SDK freshness.
- Add the proposed optional `httpx.Response.extensions["transfermarkt_fetched_at"]` contract, containing a
  naive `datetime`. A replay transport supplies the original capture clock's timestamp verbatim; ordinary responses
  use the current fetch time. Validate supplied metadata, retaining the server's existing naive timestamp convention.
- Retain stable URL construction and assembly order. Replay matches by method and full URL, including repeated
  query parameters, rather than request completion order. Missing recordings raise a caller transport exception
  and never fall back to live traffic. Exact model replay requires the same response bytes and fetch metadata;
  otherwise `updatedAt` reflects the replay fetch time. Existing snapshots strip `updatedAt`, so add assertions
  that compare it directly.

**Gate:** every supported facade method returns its declared model; concurrent calls keep freshness isolated;
record-and-replay yields equal serialized models, including `updatedAt`, with live networking disabled.

### 4. Make the server consume the facade

- Construct one `Transfermarkt` in `app/main.py` lifespan using existing environment settings and `CacheConfig`.
  Close it in `finally`. Change route dependencies and endpoint bodies to call facade methods and return models.
- Preserve route query validation, response aliases, error messages, OpenAPI contracts and rate-limit exemptions.
  Keep HTTP argument validation as `422`; the SDK's local validation does not replace FastAPI validation.
- Route countries and unsupported jersey-number calls through the same core behavior. Remove the middleware's
  freshness setup once each facade call owns its scope; keep request logging.
- Update test dependency overrides and `scripts/capture_fixtures.py` for the new boundary. Keep existing fixture
  URLs, captured response shapes and frozen v3 baselines; do not regenerate snapshots to conceal regressions.

**Gate:** all current HTTP snapshots and error/validation/rate-limit tests pass, and SDK JSON agrees with HTTP JSON
for the same recorded responses and timestamps. Server shutdown closes the shared transport.

### 5. Package and release

- Add a PEP 517 build backend, remove `tool.uv.package = false`, and explicitly include `transfermarkt_api`, `app`
  and `transfermarkt_api/py.typed` in distribution artifacts. Exclude tests, fixtures and local configuration.
- Core dependency ranges cover `httpx`, `pydantic` and `cachetools`; put FastAPI, uvicorn, `limits` and
  `pydantic-settings` in `[project.optional-dependencies].server`. Use the ADR's `pydantic>=2.13,<3` baseline;
  choose compatible bounds for the remaining dependencies from the APIs actually used. Regenerate `uv.lock`.
- Update README commands and both check/live workflows to install with `uv sync --frozen --extra server`.
  Update live-test path filters for the extracted core.
- Fix Docker installation order: copy package sources before installing the project, select the `server` extra,
  and remove `--no-install-project`. Verify the built image starts with the retained `app.main:app` entry point.
- Add CI distribution checks: build wheel and sdist; install the wheel in a clean core-only environment outside the
  checkout; run import and offline facade smoke tests without FastAPI or settings packages installed. Build a
  wheel from the sdist too. Check `py.typed` and inspect dependency metadata. Test supported Python 3.12 and 3.13.
- Add a small type-checking consumer example to verify public method return types and exported nested models.
  Check dependency compatibility with a separate application lockfile; the SDK must not force server dependencies
  or its own exact dependency pins into that environment.
- Document standalone use, model serialization, lifecycle ownership, `cache=None`, and an async transport adapter
  that records status, relevant headers, body and fetch time before returning a response for SDK parsing. Include
  replay and custom-error propagation examples. The adapter must close its backend and preserve WAF headers;
  proxy and browser-capable backends are caller choices.
- Update CHANGELOG and choose the release version using the ADR's semver policy after reviewing actual public API
  changes. Keep package and server version metadata aligned. Publishing and deployment are separate release steps;
  this implementation is complete when artifacts and release instructions are reviewable.

**Gate:** wheel and sdist work independently of the checkout, the core-only smoke test succeeds, the server extra
starts the service, and the existing offline suite and Ruff checks pass.

## Acceptance tests

Extend `tests/test_tfmkt_client.py` for SDK exceptions and client controls; add focused facade, replay and packaging
coverage. Reuse `tests/upstream.py`, `tests/cases.py` and current snapshots instead of creating another fixture set.

| Concern | Required evidence |
| --- | --- |
| Import isolation | Import public facade and schemas with server dependencies absent and hostile `TFMKT_*` variables / `.env`; no settings evaluation or I/O |
| Complete transport interception | Squad assembly records `/squad`, `/attributes`, `/players`, transfer histories and any `/clubs` batches; error responses are recorded before parsing |
| Cache controls | Default cache hits retain original timestamps; `cache=None` repeats ordinary and reference requests; errors are not cached |
| Failure classification | Unknown IDs, service-generated not-found errors, WAF, `403`, `429`, timeout, connection failure, invalid JSON/envelope and model validation each map correctly |
| Caller control | Custom circuit-open / replay-miss errors retain identity; no SDK retries; cancellation propagates and sibling tasks finish cleanup |
| Request identity | Batch sorting, deduplication, chunk boundaries and season/page parameters yield stable URLs; output keeps upstream ordering |
| Replay | Store responses before SDK parsing, replay without network access, and compare full model JSON with original fetch timestamps |
| Lifecycle and concurrency | Context exit on success/failure closes once; explicit close is idempotent; all fan-out respects the cap; client state remains isolated |
| Freshness | Simultaneous calls, sequential calls, cache hits and failed calls do not leak timestamps across operations |
| HTTP compatibility | Existing snapshots, validation `422`, unsupported endpoint `501`, exception detail bodies, rate limits and health behavior remain unchanged |
| Distribution | Core-only wheel installation, sdist rebuild, `py.typed`, type-checking example and server-extra startup work on supported Python versions |

Run the repository's offline checks with the server extra installed: `uv run ruff check .`,
`uv run ruff format --check .`, and `uv run pytest`. Live smoke tests remain an explicit upstream-access check,
not a prerequisite for proving transport injection or replay.

## Delivery order

Implement steps 1–3 on one branch so package movement, exception replacement and facade lifecycle remain coherent.
Then complete server adaptation and packaging before merging: the extraction must not ship a broken server.
Use each step's gate to localize regressions. Stop when the acceptance table passes and the documentation and
artifacts are ready; downstream orchestration and storage adapters are outside this implementation.
