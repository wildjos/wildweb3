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

import toml
from dotenv import load_dotenv

from python_backend.logger_config import LOGGER, set_logger_level

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
            LOGGER.info("Ethereum Node URL: %s  (api-key hidden)", obscured_url)

        else:
            LOGGER.info("Ethereum Node URL: %s", eth_url)
    else:
        LOGGER.info("Ethereum Node URL not found")


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
            print(f"config = {config}")
            config = resolve_env_variables(config)
            print_resolved_vars(config)
        return config

    except FileNotFoundError as e:
        LOGGER.warning("load_config: File not found error %s", e)
        return {}
