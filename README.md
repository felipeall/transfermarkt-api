# transfermarkt-api

This project provides a lightweight and easy-to-use interface for extracting data from [Transfermarkt](https://www.transfermarkt.com/) 
by applying web scraping processes and offering a RESTful API service via FastAPI. With this service, developers can 
seamlessly integrate Transfermarkt data into their applications, websites, or data analysis pipelines.

Please note that the deployed application is used only for testing purposes and has a rate limiting 
feature enabled. If you'd like to customize it, consider hosting in your own cloud service. 

### API Swagger
https://transfermarkt-api.fly.dev/

### Running Locally

````bash
# Clone the repository
$ git clone https://github.com/felipeall/transfermarkt-api.git

# Go to the project's root folder
$ cd transfermarkt-api

# Instantiate a Poetry virtual env
$ poetry shell

# Install the dependencies
$ poetry install --no-root

# (optional) Append the current directory to PYTHONPATH
$ export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start the API server
$ python app/main.py

# Access the API local page
$ open http://localhost:8000/
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
