"""
Logger configuration module.

This module provides functionality to set up and configure a global logger
based on the configuration settings provided in a dictionary. The logger
level is set according to the 'log_level' specified in the configuration.

Attributes:
    LOGGER (logging.Logger): The global logger instance.
"""

import logging
from typing import Any, MutableMapping

ConfigType = MutableMapping[str, Any]


def set_logger_level(config: ConfigType) -> None:
    """
    Set the logger level based on the configuration.

    Args:
        config (ConfigType): The configuration dictionary.

    Returns:
        None
    """
    log_level = config.get('api_server', {}).get('log_level', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level, \
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(numeric_level)
    logging.info("Logger level set to %s", log_level)


# Create a global logger instance
LOGGER = logging.getLogger(__name__)
