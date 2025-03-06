# Setup Instructions

## Environment Variables Setup

This project requires a `.env` file to store sensitive information such as Ethereum private keys and API keys. This file should *not* be committed to version control.

### Creating the .env File

In the project root directory, create a file named `.env`.

Add the following environment variables:
```
INFURA_API_KEY=your_infura_api_key
PRIVATE_KEY=your_private_key
ALICE_PRIVATE_KEY=alice_private_key
BOB_PRIVATE_KEY=bob_private_key
CHARLIE_PRIVATE_KEY=charlie_private_key
```

### Using the .env.example File

A `.env.example` file is provided as a template for the required environment variables. You can copy this file to create your own `.env` file:

```sh
cp .env.example .env
```

Then fill in the actual values for the environment variables in the `.env` file.

### Placement of the .env File

The `.env` file should be placed in the project root directory. The `load_dotenv()` function will look for the `.env` file in the current working directory or any parent directory. This means you can run the code from the `python-backend` directory or the project root directory, and the environment variables will be loaded correctly.


### Using .env in Docker

The `.env` file is automatically mounted in the Docker containers using Docker Compose. Ensure it exists before running the application.

### Docker Compose Mounting

The `docker-compose.yml` file includes:

```yaml
env_file:
  - .env
```

This ensures the environment variables are available inside the running containers.

### Environment Variable Substitution

The environment variables defined in the `.env` file are substituted into the `config.toml` file when it is loaded. This allows you to use placeholders in the `config.toml` file that are replaced with the actual values from the environment variables.

For example, in the `config.toml` file, there's an api-key:

```toml
eth_url = "https://sepolia.infura.io/v3/${INFURA_API_KEY}"
```

When the configuration is loaded, `${INFURA_API_KEY}` will be replaced with the actual value from the `.env` file.
