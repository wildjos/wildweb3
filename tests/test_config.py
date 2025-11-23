"""
Unit tests for the config module in the python_backend.
"""
import unittest
import os
import sys
from unittest.mock import patch, mock_open
import toml

# Add the path to the python_backend explicitly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_backend')))

from python_backend.core.config import load_config, resolve_env_variables, \
    print_resolved_vars # pylint: disable=C0413


class TestConfig(unittest.TestCase):
    """
    Test cases for the functions in the config module.

    This class contains unit tests for the following functions:
    - resolve_env_variables: Recursively replace placeholders with actual environment variables.
    - print_resolved_vars: Print resolved environment variables, obscuring sensitive information.
    - load_config: Load configuration from a TOML file.
    """

    def setUp(self):
        """Set up environment variables for testing."""
        os.environ["INFURA_API_KEY"] = "api_key_here"
        os.environ["TENDERLY_TESTNET_ID"] = "testnet_id_here"
        os.environ["TENDERLY_EXPLORER_KEY"] = "explorer_key_here"
        os.environ["PRIVATE_KEY"] = "your_key_here"
        os.environ["ALICE_PRIVATE_KEY"] = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        os.environ["BOB_PRIVATE_KEY"] = "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        os.environ["CHARLIE_PRIVATE_KEY"] = "0xcccccccccccccccccccccccccccccccccc"

        self.mock_toml_data = """
        [api_server]
        app_name    = "wildweb3_api:app"
        host        = "0.0.0.0"
        port        = 8040
        log_level   = "debug"
        reload      = false

        [networks.sepolia]
        name        = "sepolia"
        url         = "https://sepolia.infura.io/v3/${INFURA_API_KEY}"
        chain_id    = 11155111
        explorer    = "https://sepolia.etherscan.io"

        [networks.wildjos_vtn]
        name        = "wildjos_vtn"
        url         = "https://virtual.sepolia.rpc.tenderly.co/${TENDERLY_TESTNET_ID}"
        chain_id    = 111777111
        explorer    = "https://dashboard.tenderly.co/explorer/vnet/${TENDERLY_EXPLORER_KEY}"

        [accounts]
        alice   = { address = "0xAliceEthereumAddress", private_key = "${ALICE_PRIVATE_KEY}" }
        bob     = { address = "0xBobEthereumAddress", private_key = "${BOB_PRIVATE_KEY}" }
        charlie = { address = "0xCharlieEthereumAddress", private_key = "${CHARLIE_PRIVATE_KEY}" }
        """

        self.expected_resolved_config = {
            "api_server": {
                "app_name": "wildweb3_api:app",
                "host": "0.0.0.0",
                "port": 8040,
                "log_level": "debug",
                "reload": False
            },
            "networks": {
                "sepolia": {
                    "name": "sepolia",
                    "url": "https://sepolia.infura.io/v3/api_key_here",
                    "chain_id": 11155111,
                    "explorer": "https://sepolia.etherscan.io"
                },
                "wildjos_vtn": {
                    "name": "wildjos_vtn",
                    "url": "https://virtual.sepolia.rpc.tenderly.co/testnet_id_here",
                    "chain_id": 111777111,
                    "explorer": "https://dashboard.tenderly.co/explorer/vnet/explorer_key_here"
                }
            },
            "accounts": {
                "alice": {
                    "address": "0xAliceEthereumAddress",
                    "private_key": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                },
                "bob": {
                    "address": "0xBobEthereumAddress",
                    "private_key": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
                },
                "charlie": {
                    "address": "0xCharlieEthereumAddress",
                    "private_key": "0xcccccccccccccccccccccccccccccccccc"
                }
            }
        }


    @patch("builtins.open", new_callable=mock_open, read_data="[mocked]")
    @patch("toml.load")
    @patch("python_backend.config.set_logger_level")  # Prevent actual logging changes
    def test_load_config(self, mock_set_logger, mock_toml_load, mock_file_open):
        """Test that load_config correctly loads, processes, and resolves env variables."""
        mock_toml_load.return_value = toml.loads(self.mock_toml_data)

        with patch("python_backend.config.print_resolved_vars") as mock_print:
            config = load_config("dummy_path")


        # Check that the file was opened correctly
        mock_file_open.assert_called_once_with("dummy_path", "r", encoding="utf-8")
        # Check that toml.load() was called
        mock_toml_load.assert_called_once()
        # Ensure logger level setter was called
        mock_set_logger.assert_called_once_with(mock_toml_load.return_value)
        # Ensure print_resolved_vars was called
        mock_print.assert_called_once()
        # Verify the final resolved config
        self.assertEqual(config, self.expected_resolved_config)

        for call in mock_set_logger.call_args_list:
            print(call)


    def test_resolve_env_variables(self):
        """Test that environment variables in the config get correctly replaced."""
        resolved = resolve_env_variables(toml.loads(self.mock_toml_data))
        self.assertEqual(resolved, self.expected_resolved_config)


    @patch("python_backend.logger_config.LOGGER.info")
    def test_print_resolved_vars(self, mock_logger):
        """Test that print_resolved_vars correctly obscures sensitive information."""
        print_resolved_vars(self.expected_resolved_config)

        # Check that it logged the expected obscured URL format
        mock_logger.assert_any_call("Node URL: %s  (api-key hidden)", \
                                    "https://sepolia.infura.io/v3/api_.....here")
        mock_logger.assert_any_call("Explorer URL: %s  (api-key hidden if applicable)", \
                                    "https://sepolia.etherscan.io")
        mock_logger.assert_any_call("Node URL: %s  (api-key hidden)", \
                                    "https://virtual.sepolia.rpc.tenderly.co/test.....here")
        mock_logger.assert_any_call("Explorer URL: %s  (api-key hidden if applicable)", \
                                    "https://dashboard.tenderly.co/explorer/vnet/expl.....here")


        # Check that private keys were obscured
        mock_logger.assert_any_call("%s: %s / %s... (hidden)", "alice", \
                                    "0xAliceEthereumAddress", "0xaaa")
        mock_logger.assert_any_call("%s: %s / %s... (hidden)", "bob", \
                                    "0xBobEthereumAddress", "0xbbb")
        mock_logger.assert_any_call("%s: %s / %s... (hidden)", "charlie", \
                                    "0xCharlieEthereumAddress", "0xccc")


    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch("python_backend.logger_config.LOGGER.warning")  # Prevent unnecessary logging
    def test_load_config_file_not_found(self, mock_logger, _):
        """Test that load_config returns an empty dict when the file is missing."""

        config = load_config("missing.toml")

        for call in mock_logger.call_args_list:
            print(call)

        # Assert that a warning was logged
        mock_logger.assert_called_once()
        # Ensure function returned an empty dict
        self.assertEqual(config, {})


if __name__ == "__main__":
    unittest.main()
