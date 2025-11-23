"""
Configuration module.

This module provides functionality to load and resolve configuration settings
from environment variables and a TOML file. It also sets up logging based on
the configuration.

Attributes:
    ConfigType (MutableMapping[str, Any]): Type alias for configuration dictionary.
"""

import os
import re
from typing import Any, MutableMapping, Dict, Union
from urllib.parse import urlparse, urlunparse

import toml
from dotenv import load_dotenv

from core.logger_config import LOGGER, set_logger_level

ConfigType = MutableMapping[str, Any]

# Load environment variables from .env
load_dotenv()


def resolve_env_variables(data: Union[Dict[str, Any], str]) -> Union[Dict[str, Any], str]:
    """
    Recursively replace placeholders with actual environment variables.

    Args:
        data (Union[Dict[str, Any], str]): The data to resolve environment variables in.

    Returns:
        Union[Dict[str, Any], str]: The data with resolved environment variables.
    """
    if isinstance(data, dict):
        return {k: resolve_env_variables(v) for k, v in data.items()}

    # Only process strings
    if isinstance(data, str):
        pattern = re.compile(r'\$\{([^}]+)\}')
        matches = pattern.findall(data)
        for match in matches:
            # Keep the placeholder if the env var is missing
            env_value = os.getenv(match, f"${{{match}}}")
            data = data.replace(f"${{{match}}}", env_value)
        return data

    # Return unchanged for int, float, bool
    return data



def obscure_api_key(url: str) -> str:
    """
    Obscures the sensitive part (e.g., API key or identifier) in a URL.

    Args:
        url (str): The URL containing the sensitive part.

    Returns:
        str: The URL with the sensitive part obscured.
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')

    # Identify and obscure the sensitive part in the path
    for i, part in enumerate(path_parts):
        if len(part) > 10:  # Assume sensitive parts are long strings (e.g. API keys)
            path_parts[i] = f"{part[:4]}.....{part[-4:]}"

    # Reconstruct the URL with the obscured path
    obscured_path = '/'.join(path_parts)
    obscured_url = urlunparse(parsed_url._replace(path=obscured_path))
    return obscured_url


def print_resolved_vars(config: ConfigType) -> None:
    """
    Print resolved environment variables, obscuring sensitive information.

    Args:
        config (ConfigType): The configuration dictionary.

    Returns:
        None
    """
    LOGGER.info("config = %s", config)
    # Extract accounts dictionary with address-private key pairs
    accounts = config.get("accounts", {})

    # Print resolved accounts (hiding private key details for security)
    for name, details in accounts.items():
        LOGGER.info("%s: %s / %s... (hidden)", name, details['address'], details['private_key'][:5])

    networks = config.get("networks", {})
    if networks:
        for network_name, network_details in networks.items():
            LOGGER.info("Network: %s", network_name)

            # Handle node URL
            node_url = network_details.get("url", "")
            if node_url:
                obscured_url = obscure_api_key(node_url)
                LOGGER.info("Node URL: %s  (api-key hidden)", obscured_url)
            else:
                LOGGER.info("Node URL not found for %s", network_name)

            # Handle explorer URL
            explorer_url = network_details.get("explorer", "")
            if explorer_url:
                obscured_explorer = obscure_api_key(explorer_url)
                LOGGER.info("Explorer URL: %s  (api-key hidden if applicable)", obscured_explorer)
            else:
                LOGGER.info("Explorer URL not found for %s", network_name)


def load_config(filename: str) -> ConfigType:
    """
    Load configuration from a TOML file.

    Args:
        filename (str): The path to the TOML file.

    Returns:
        ConfigType: The loaded configuration dictionary.
    """
    try:
        with open(filename, "r", encoding='utf-8') as f:
            config = toml.load(f)
            set_logger_level(config)
            config = resolve_env_variables(config)
            print_resolved_vars(config)
        return config

    except FileNotFoundError as e:
        LOGGER.warning("load_config: File not found error %s", e)
        return {}


class InvalidNetworkException(Exception):
    """
    Custom exception raised when an invalid network is provided.
    """
    def __init__(self, network_name: str):
        super().__init__(f"Invalid network: {network_name}")
        self.network_name = network_name

def get_updated_config(config: dict, network_name: str) -> dict:
    """
    Validates the network name and updates the configuration with the selected network.

    Args:
        config (dict): The application configuration dictionary.
        network_name (str): The name of the network to validate and use.

    Returns:
        dict: A copy of the configuration updated with the selected network.

    Raises:
        InvalidNetworkException: If the specified network is invalid.
    """
    networks = config.get("networks", {})
    if network_name not in networks:
        raise InvalidNetworkException(network_name)

    updated_config = config.copy()
    updated_config["network"] = networks[network_name]
    return updated_config
