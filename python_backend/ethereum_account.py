"""
This module handles Ethereum account management, including private key management,
Web3 connection, and transaction signing and sending.
"""
from web3 import Web3
from web3.types import TxParams, SignedTx
from eth_account import Account
from python_backend.logger_config import LOGGER


class EthereumAccount:
    """
    Handles the Ethereum account, including private key management and Web3 connection.
    """

    def __init__(self, user: str, config: dict):
        self.user = user
        self.config = config

        user_config = self.config.get("accounts", {}).get(self.user)
        if not user_config:
            raise ValueError(f"User '{self.user}' not found in the configuration")

        self.private_key = user_config.get("private_key")
        if not self.private_key:
            raise ValueError(f"Private key for user '{self.user}' is missing in configuration")

        self.w3 = self._connect_to_infura()
        self.account = Account().from_key(self.private_key)


    def _connect_to_infura(self) -> Web3:
        """
        Connect to the Infura Sepolia node.

        Returns:
            Web3: The Web3 instance connected to the Infura Sepolia node.

        Raises:
            ConnectionError: If unable to connect to the Ethereum node.
        """
        eth_node_url = self.config['network']['eth_url']
        w3 = Web3(Web3.HTTPProvider(eth_node_url))

        if not w3.is_connected():
            raise ConnectionError("Failed to connect to the Ethereum node")

        LOGGER.info("Connected to Ethereum node: %s", eth_node_url)
        return w3


    def get_balance(self) -> int:
        """Retrieve the balance of the Ethereum account in Wei."""
        return self.w3.eth.get_balance(self.account.address)


    def get_nonce(self) -> int:
        """Retrieve the current nonce for the Ethereum account."""
        return self.w3.eth.get_transaction_count(self.account.address)


    def get_gas_price(self) -> int:
        """Retrieve the current gas price from the Ethereum network."""
        return self.w3.eth.gas_price


    def sign_transaction(self, transaction: TxParams) -> SignedTx:
        """
        Sign a transaction using the account's private key.

        Args:
            transaction (TxParams): The transaction dictionary to be signed.

        Returns:
            SignedTransaction: The signed transaction object.
        """
        signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
        LOGGER.info("Transaction signed: Nonce %d, Gas Price %d", \
                    transaction["nonce"], transaction["gasPrice"])
        return signed_tx


    def send_transaction(self, signed_tx: SignedTx) -> str:
        """
        Send a signed Ethereum transaction.

        Args:
            signed_tx (SignedTransaction): The signed transaction object.

        Returns:
            str: The transaction hash as a hexadecimal string.
        """
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        LOGGER.info("Transaction sent: %s", tx_hash.hex())
        return tx_hash.hex()


    def from_wei(self, value: int, unit: str) -> float:
        """
        Convert a value from Wei to the specified unit.

        Args:
            value (int): The value in Wei to be converted.
            unit (str): The unit to convert to (e.g., 'ether', 'gwei').

        Returns:
            float: The converted value.
        """
        return self.w3.from_wei(value, unit)
