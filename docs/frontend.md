# Frontend

The frontend uses Streamlit to provide an interactive UI for compiling, deploying, and interacting with Solidity smart contracts.

## Configuration

The frontend communicates with the backend service using the `BACKEND_URL` environment variable. This environment variable is set in the `docker-compose.yml` file:

```yaml
services:
  frontend:
    environment:
      - BACKEND_URL=http://python-backend:8040
```

This configuration allows the frontend to connect to the backend service using the specified URL.

## Building and Running the Frontend

Before building and running the frontend, make sure you have followed the [Setup Instructions](setup.md) to create the necessary configuration files and environment variables.

### Building the Docker Image

Navigate to the `frontend` directory and build the Docker image using the following command:

```sh
cd /path/to/wildweb3/frontend
docker build -t wildweb3-frontend .
```

### Running the Docker Container

Run the Docker container with the necessary environment variables:

```sh
docker run -p 8501:8501 wildweb3-frontend
```

Replace `/path/to/wildweb3` with the actual path to your project root.

### Running the Frontend from the Command Line

You can also run the frontend directly from the command line:

```sh
streamlit run app.py
```

This will start the Streamlit server, and you can access the frontend by navigating to `http://localhost:8501` in your web browser.

### Using Docker Compose

You can use Docker Compose to build and run both the frontend and backend services. Navigate to the project root directory and use Docker Compose to build and run the services:

```sh
docker-compose up --build
```

This command will build and start both the `python-backend` and `frontend` services.

### Accessing the Frontend

Once the services are running, you can access the frontend by navigating to `http://localhost:8501` in your web browser.

### Using the Frontend

The frontend provides three main functionalities:

1. **Compile Smart Contract**:
   - Navigate to the "Compile" page using the sidebar.
   - Click the "Compile" button to compile the smart contract.
   - The response from the backend will be displayed.

2. **Deploy Smart Contract**:
   - Navigate to the "Deploy" page using the sidebar.
   - Click the "Deploy" button to deploy the smart contract.
   - The response from the backend will be displayed, including the contract address.

3. **Interact with Smart Contract**:
   - Navigate to the "Interact" page using the sidebar.
   - Enter the contract address in the provided text input.
   - Click the "Call Function" button to interact with the smart contract.
   - The response from the backend will be displayed.