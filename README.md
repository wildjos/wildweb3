# WildWeb3

WildWeb3 is my space for experimenting with smart contracts, testing Web3 ideas, and documenting tricky implementations. This project is a sandbox where I explore different aspects of blockchain development, keep examples of interesting Solidity contracts, and try out some different things.

## What’s Inside?

🔍 Smart Contract Experiments – A collection of cool, tricky, and sometimes useful Solidity examples.

💡 Web3 Testing Ground – A place to test contracts.

🖥 Interactive UI – A Streamlit-powered frontend for user ease of use.

⚙️ REST API Backend – Uses FastAPI to drive compilation, deployment, and contract interaction.

📦 Dockerized Setup – Ensuring an isolated and reproducible development environment.

🛡 Security Practices – Experiments with key management, Infura API usage, and best practices.

🚀 Future Expansion – Eventually exploring Rust for Web3 backend services or contract compilation.


WildWeb3 is not a polished framework — it's my place for testing ideas, trying things out, and recording my blockchain development journey.


## Environment Variables Setup

This project requires a `.env` file to store sensitive information such as Ethereum private keys and API keys. This file should *not* be committed to version control and will be mounted via Docker.

### Creating the .env File

In the project root directory, create a file named `.env`.

Add the following environment variables:
```
INFURA_API_KEY=your_infura_api_key
PRIVATE_KEY=your_private_key
```

### Using .env in Docker

The .env file is automatically mounted in the Docker containers using Docker Compose. Ensure it exists before running the application.

### Docker Compose Mounting

The docker-compose.yml file includes:
```
env_file:
  - .env
```

This ensures the environment variables are available inside the running containers.

