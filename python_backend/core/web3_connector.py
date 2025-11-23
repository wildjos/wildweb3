'''
web3_connector.py

This module provides the Web3Connector class, which facilitates connections to Ethereum networks
using the Web3.py library. It allows for easy configuration and management of Web3 instances
based on network details provided in a configuration dictionary.
'''
from web3 import Web3
from core.logger_config import LOGGER

class Web3Connector:
    """
    Handles Web3 connections to different Ethereum networks based on configuration.
    """

    def __init__(self, network_config: dict):
        """
        Initialize the Web3Connector with a given network configuration.

        Args:
            network_config (dict): A dictionary containing network connection details.
        """
        self.network_config = network_config
        self.w3 = self._connect()


    def _connect(self) -> Web3:
        """
        Establish a connection to the Ethereum network.

        Returns:
            Web3: An instance of Web3 connected to the specified network.

        Raises:
            ConnectionError: If unable to connect to the Ethereum node.
        """
        node_url = self.network_config.get("url")
        if not node_url:
            raise ValueError("Node URL is missing in network configuration")

        w3 = Web3(Web3.HTTPProvider(node_url))

        if not w3.is_connected():
            raise ConnectionError(f"Failed to connect to the Ethereum node at {node_url}")

        LOGGER.info("Connected to Ethereum node: %s", node_url)
        return w3


    def get_web3(self) -> Web3:
        """Return the connected Web3 instance."""
        return self.w3


    def get_network_config(self) -> dict:
        """Return the network configuration."""
        return self.network_config
