# Python Backend

The Python backend uses FastAPI to drive compilation, deployment, and interaction with Solidity smart contracts.

## Building and Running the Python Backend

Before building and running the backend, make sure you have followed the [Setup Instructions](setup.md) to create the necessary configuration files and environment variables.

### Building the Docker Image

Navigate to the `python-backend` directory and build the Docker image using the following command:

```sh
cd /path/to/wildweb3/python-backend
docker build -t wildweb3-python-backend .
```

### Running the Docker Container

Run the Docker container with the `data` directory mounted to ensure the `config.toml` file is available:

```sh
docker run -v /path/to/wildweb3/data:/app/data -p 8040:8040 wildweb3-python-backend
```

Replace `/path/to/wildweb3` with the actual path to your project root.

### Running the Backend from the Command Line

You can also run the backend directly from the command line by specifying the path to the configuration file using the `--config` argument:

```sh
python main.py --config /path/to/wildweb3/data/config.toml
```

Replace `/path/to/wildweb3` with the actual path to your project root.

This allows you to run the backend with different configuration files depending on the environment (e.g., Docker or local development).