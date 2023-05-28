# transfermarkt-api

API service to get data from [Transfermarkt](https://www.transfermarkt.com/)


### API Swagger
https://transfermarkt-api.vercel.app/

### Running Locally

````bash
# Clone the repository
$ git clone https://github.com/felipeall/transfermarkt-api.git

# Go to the project's root folder
$ cd transfermarkt-api

# Instantiate a Poetry virtual env
$ poetry shell

# Install the dependencies
$ poetry install

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
