# transfermarkt-api

A RESTful API (FastAPI) for football data from [Transfermarkt](https://www.transfermarkt.com/): players, clubs and competitions.

Since version 4.0.0, data comes from Transfermarkt's JSON API (`tmapi.transfermarkt.technology`), the same API the website uses, instead of scraping HTML pages. The website blocks requests from most cloud hosts, which broke v3 deployments; the JSON API does not. See [CHANGELOG.md](CHANGELOG.md) for what changed in the response format.

Please note that the deployed application is used only for testing purposes and has a rate limiting
feature enabled. If you'd like to customize it, consider hosting in your own cloud service.

The JSON API is internal to Transfermarkt and undocumented: it can change without notice. This project's MIT license covers its code, not the data; check [Transfermarkt's terms](https://www.transfermarkt.com/intern/) before using the data in your own services.

### API Swagger
https://transfermarkt-api.fly.dev/

### Endpoints

| Endpoint | Notes |
| --- | --- |
| `GET /players/search/{player_name}?page_number=` | 10 results per page |
| `GET /players/{player_id}/profile` | |
| `GET /players/{player_id}/market_value` | |
| `GET /players/{player_id}/transfers` | |
| `GET /players/{player_id}/stats` | Per season, competition and club; club competitions only |
| `GET /players/{player_id}/injuries?page_number=` | 15 injuries per page |
| `GET /players/{player_id}/achievements` | `501`: no data source |
| `GET /players/{player_id}/jersey_numbers` | `501`: no data source |
| `GET /clubs/search/{club_name}?page_number=` | 10 results per page |
| `GET /clubs/{club_id}/profile` | |
| `GET /clubs/{club_id}/players?season_id=` | Current squad by default |
| `GET /competitions/search/{competition_name}?page_number=` | 10 results per page |
| `GET /competitions/{competition_id}/clubs?season_id=` | Current season by default |

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
| `RATE_LIMITING_FREQUENCY`     | Delay allowed between each API call. See [slowapi](https://slowapi.readthedocs.io/en/latest/) for more | `2/3seconds`                             |
| `TFMKT_BASE_URL`              | Transfermarkt JSON API base URL                                                                        | `https://tmapi.transfermarkt.technology` |
| `TFMKT_TIMEOUT_SECONDS`       | Timeout for each upstream request                                                                      | `15`                                     |
| `TFMKT_MAX_CONCURRENCY`       | Maximum concurrent upstream requests across the whole server                                          | `10`                                     |
| `CACHE_TTL_SECONDS`           | How long successful upstream responses are cached                                                      | `600`                                    |
| `CACHE_REFERENCE_TTL_SECONDS` | Cache duration for reference data (countries, positions, ...)                                          | `86400`                                  |
| `CACHE_MAX_ENTRIES`           | Maximum number of cached upstream responses                                                            | `2000`                                   |
