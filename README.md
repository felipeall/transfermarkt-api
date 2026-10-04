# transfermarkt-api

A RESTful API (FastAPI) for football data from [Transfermarkt](https://www.transfermarkt.com/): players, clubs and competitions.

Since version 4.0.0, data comes from Transfermarkt's JSON API (`tmapi.transfermarkt.technology`), the same API the website uses, instead of scraping HTML pages. The website blocks requests from most cloud hosts, which broke v3 deployments; the JSON API does not. See [CHANGELOG.md](CHANGELOG.md) for what changed in the response format.

Please note that the deployed application is used only for testing purposes and is rate limited to 2 requests
every 3 seconds per client IP. If you'd like to customize it, consider hosting in your own cloud service.

The JSON API is internal to Transfermarkt and undocumented: it can change without notice. This project's MIT license covers its code, not the data; check [Transfermarkt's terms](https://www.transfermarkt.com/intern/) before using the data in your own services.

### API Swagger
https://transfermarkt-api.fly.dev/

### Endpoints

| Endpoint | Notes |
| --- | --- |
| `GET /players/search/{player_name}?page_number=` | 10 results per page |
| `GET /players/{player_id}/profile` | |
| `GET /players/{player_id}/market_value` | |
| `GET /players/{player_id}/transfers` | Transfer type, age, contract dates, remaining contract days, and each club's league and country at the time |
| `GET /players/{player_id}/stats` | Per season, competition and club; club competitions only |
| `GET /players/{player_id}/matches?season_id=&page_number=` | Past matches of the player's teams, most recent first, 50 per page; no upcoming fixtures |
| `GET /players/{player_id}/injuries?page_number=` | 15 injuries per page |
| `GET /players/{player_id}/absences?page_number=` | Suspensions, call-ups, leave; 15 per page |
| `GET /players/{player_id}/achievements` | Titles and awards with season, club and competition |
| `GET /players/{player_id}/national_career` | Senior and youth national teams |
| `GET /players/{player_id}/jersey_numbers` | `501`: no data source |
| `GET /countries/` | Country IDs and metadata, including historical entries; cached for 24 hours |
| `GET /clubs/?country_id=` | Available club IDs and names for a country; limited upstream coverage, no pagination |
| `GET /clubs/search/{club_name}?page_number=` | 10 results per page |
| `GET /clubs/{club_id}/profile` | Squad value details, historical names and stadium details |
| `GET /clubs/{club_id}/players?season_id=` | Current squad by default; shirt number and captaincy for the selected season |
| `GET /clubs/{club_id}/achievements` | Club titles by season |
| `GET /coaches/search/{coach_name}?page_number=` | 10 results per page |
| `GET /coaches/{coach_id}/profile` | |
| `GET /competitions/search/{competition_name}?page_number=` | 10 results per page |
| `GET /competitions/{competition_id}/clubs?season_id=` | Current season by default |
| `GET /competitions/{competition_id}/table?season_id=` | League table; one table per group for group stages |
| `GET /competitions/{competition_id}/seasons` | Valid `season_id` values |
| `GET /games/{game_id}` | Score, lineups, coaches, stadium, team stats, goals, cards and substitutions |

Errors: `404` unknown ID, `501` endpoint without data source, `502` unexpected upstream response, `503` upstream blocked or refused the request, `504` upstream timeout.

Fields without an upstream value are returned as `null`. `updatedAt` is when the underlying data was fetched from Transfermarkt; responses are cached for 10 minutes by default.

### Running Locally

Requires [uv](https://docs.astral.sh/uv/).

````bash
# Clone the repository
$ git clone https://github.com/felipeall/transfermarkt-api.git

# Go to the project's root folder
$ cd transfermarkt-api

# Install Python 3.12 and the dependencies
$ uv sync

# Start the API server
$ uv run uvicorn app.main:app --reload

# Access the API local page
$ open http://localhost:8000/
````

### Running Tests

````bash
# Offline tests (recorded upstream responses, no network)
$ uv run pytest

# Live smoke tests against Transfermarkt's JSON API
$ uv run pytest -m live

# Re-record upstream fixtures and response snapshots
$ rm -rf tests/fixtures/tfmkt && uv run python scripts/capture_fixtures.py
````

### Running via Docker

````bash
# Clone the repository
$ git clone https://github.com/felipeall/transfermarkt-api.git

# Go to the project's root folder
$ cd transfermarkt-api

# Build the Docker image
$ docker build -t transfermarkt-api .

# Instantiate the Docker container
$ docker run -d -p 8000:8000 transfermarkt-api

# Access the API local page
$ open http://localhost:8000/
````

### Environment Variables

| Variable                      | Description                                                                                            | Default                                  |
|-------------------------------|--------------------------------------------------------------------------------------------------------|------------------------------------------|
| `RATE_LIMITING_ENABLE`        | Enable rate limiting feature for API calls                                                             | `false`                                  |
| `RATE_LIMITING_FREQUENCY`     | Requests allowed per client IP across all routes, in [limits notation](https://limits.readthedocs.io/en/stable/quickstart.html#rate-limit-string-notation) | `2/3seconds`                             |
| `TFMKT_BASE_URL`              | Transfermarkt JSON API base URL                                                                        | `https://tmapi.transfermarkt.technology` |
| `TFMKT_TIMEOUT_SECONDS`       | Timeout for each upstream request                                                                      | `15`                                     |
| `TFMKT_MAX_CONCURRENCY`       | Maximum concurrent upstream requests across the whole server                                          | `10`                                     |
| `CACHE_TTL_SECONDS`           | How long successful upstream responses are cached                                                      | `600`                                    |
| `CACHE_REFERENCE_TTL_SECONDS` | Cache duration for reference data (countries, positions, ...)                                          | `86400`                                  |
| `CACHE_MAX_ENTRIES`           | Maximum number of cached upstream responses                                                            | `2000`                                   |

Rate limits apply to the API routes only: `/health`, the docs (`/`, `/docs`, `/redoc`) and `/openapi.json` are not
counted. They are counted per client IP: the `Fly-Client-IP` header set by the Fly.io proxy, or the address of the
connection when that header is missing. `X-Forwarded-For` is not trusted. Behind another reverse proxy, all
requests share the proxy's address, and outside Fly.io clients can send `Fly-Client-IP` themselves, so adjust
`client_ip` in `app/main.py` before enabling rate limiting on another host.
