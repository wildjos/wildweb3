import os
import toml
import re
import logging
from typing import Any, MutableMapping
from dotenv import load_dotenv


LOGGER = logging.getLogger(__name__)
ConfigType = MutableMapping[str, Any]

# Load environment variables from .env
load_dotenv()

def set_logger_level(config: ConfigType):
    log_level = config.get('api_server', {}).get('log_level', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOGGER.setLevel(numeric_level)
    LOGGER.info(f"Logger level set to {log_level}")


# Replace placeholders with actual environment variables
#   by recursively replacing ${SECRET} with actual environment values.
def resolve_env_variables(data):
    if isinstance(data, dict):
        return {k: resolve_env_variables(v) for k, v in data.items()}
    
    elif isinstance(data, str):
        # Use regular expression to find all ${...} placeholders
        pattern = re.compile(r'\$\{([^}]+)\}')
        matches = pattern.findall(data)
        for match in matches:
            env_value = os.getenv(match, f"${{{match}}}")
            data = data.replace(f"${{{match}}}", env_value)
        return data
    
    return data


def print_resolved_vars(config):
    # Extract accounts dictionary with address-private key pairs
    accounts = config.get("accounts", {})

    # Print resolved accounts (hiding private key details for security)
    for name, details in accounts.items():
        LOGGER.info(f"{name}: {details['address']} / {details['private_key'][:5]}... (hidden)")

    # Obscure the key in the Ethereum Node URL
    eth_url = config.get('network', {}).get('eth_url', '')
    if eth_url:
        # Find the key part in the URL
        key_start = eth_url.find('/v3/') + 4
        key_end = len(eth_url)
        if key_start != -1 and key_end != -1:
            key = eth_url[key_start:key_end]
            obscured_key = key[:4] + '.....' + key[-3:]
            obscured_url = eth_url[:key_start] + obscured_key
            LOGGER.info(f"Ethereum Node URL: {obscured_url}  (api-key hidden)")
        else:
            LOGGER.info(f"Ethereum Node URL: {eth_url}")
    else:
        LOGGER.info("Ethereum Node URL not found")



# Load config from the toml file
def load_config(filename: str) -> ConfigType:

    try: 
        with open(filename, "r") as f:
            config = toml.load(f)
            set_logger_level(config)
            config = resolve_env_variables(config)
            print_resolved_vars(config)
        return config
    
    except FileNotFoundError as e:
        LOGGER.warning(f"load_config: File not found error {e}")
        return {}
    



