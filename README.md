# transfermarkt-api

This project provides a lightweight and easy-to-use interface for extracting data from [Transfermarkt](https://www.transfermarkt.com/) 
by applying web scraping processes and offering a RESTful API service via FastAPI. With this service, developers can 
seamlessly integrate Transfermarkt data into their applications, websites, or data analysis pipelines.

Please note that the deployed application is used only for testing purposes and has a rate limiting 
feature enabled. If you'd like to customize it, consider hosting in your own cloud service. 

### API Swagger
https://transfermarkt-api.fly.dev/

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
# Offline tests (recorded upstream pages, no network)
$ uv run pytest

# Live smoke tests against Transfermarkt
$ uv run pytest -m live

# Re-record upstream fixtures and response snapshots (needs an IP the Transfermarkt WAF does not block)
$ uv run python scripts/capture_fixtures.py
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

| Variable                  | Description                                               | Default      |
|---------------------------|-----------------------------------------------------------|--------------|
| `RATE_LIMITING_ENABLE`    | Enable rate limiting feature for API calls                | `false`      |
| `RATE_LIMITING_FREQUENCY` | Delay allowed between each API call. See [slowapi](https://slowapi.readthedocs.io/en/latest/) for more | `2/3seconds` |
