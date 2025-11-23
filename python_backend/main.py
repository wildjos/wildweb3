"""
WildWeb3 Python Backend main module.

This module contains the entry point for running the WildWeb3 Python backend server.
"""

import argparse
from typing import Dict, Union
import uvicorn

from core.config import load_config
from api.app import create_app


def run_webserver(config: Dict[str, Union[str, int, bool]]) -> None:
    """
    Run the web server using the provided configuration.

    Args:
        config (dict): The configuration dictionary for the web server.
    """

    server_config = uvicorn.Config(
        app=create_app(config),
        host=config["api_server"]["host"],
        port=config["api_server"]["port"],
        log_level=config["api_server"]["log_level"],
        reload=config["api_server"]["reload"],
        workers=1)

    server = uvicorn.Server(server_config)
    server.run()


def main(config_file: str) -> None:
    """
    Main function to load the configuration and run the web server.

    Args:
        config_file (str): The path to the configuration file.
    """
    # Load the configuration
    config = load_config(config_file)

    # Run the web server
    run_webserver(config)


# Entry Point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WildWeb3 Python Backend")
    parser.add_argument(
        "--config",
        type=str,
        default="../data/config.toml",
        help="Path to the configuration file"
    )

    args = parser.parse_args()
    print("Welcome to WildWeb3 python backend")

    main(args.config)
