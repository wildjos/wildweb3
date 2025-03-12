"""
Module for deploying Solidity contracts.
"""

# import os
import time
import json
from typing import List, Tuple, Any
from web3 import Web3
from web3.exceptions import TransactionNotFound
# from eth_account.signers.local import LocalAccount
from eth_account import Account

from python_backend.logger_config import LOGGER

class ContractDeployer:
    """
    Class for deploying Solidity contracts.
    """

    def __init__(self, base_filename: str, user: str, constructor_args: list, config: dict):
        """
        Initialize the ContractDeployer.

        Args:
            base_filename (str): The base filename of the contract's ABI and BIN files.
            user (str): Ther user deploying the contract.
            constructor_args (List[Any]): The arguments for the contract's constructor.
            config (dict): The configuration dictionary
        """
        self.config = config
        self.user = user
        self.constructor_args = constructor_args

        # Look up the user in the configuration
        user_config = self.config.get("accounts", {}).get(self.user)

        if not user_config:
            raise ValueError(f"User '{self.user}' not found in the configuration")

        self.pkey = user_config.get("private_key")
        if not self.pkey:
            raise ValueError(f"Private key for user '{self.user}' is not set in the configuration")

        pkey = self.pkey
        self.w3 = self.connect_to_infura()
        contract_abi, contract_bin = self.load_contract_files(base_filename)
        self.contract = self.w3.eth.contract(abi=contract_abi, bytecode=contract_bin)

        assert isinstance(pkey, str) and len(pkey) > 0, "Private key is invalid or missing!"
        self.contract_account = Account().from_key(pkey)


    def connect_to_infura(self) -> Web3:
        """
        Connect to the Infura Sepolia node.

        Returns:
            Web3: The Web3 instance connected to the Infura Sepolia node.

        Raises:
            ValueError: If the INFURA_API_KEY environment variable is not set.
            ConnectionError: If unable to connect to the Ethereum node.
        """
        eth_node_url = self.config['network']['eth_url']

        w3 = Web3(Web3.HTTPProvider(eth_node_url))
        if not w3.is_connected():
            raise ConnectionError("Failed to connect to the Ethereum node")

        LOGGER.info("EthNodeUrl: %s is connected: %s", eth_node_url, w3.is_connected())
        return w3


    def load_contract_files(self, base_filename: str) -> Tuple[List[Any], str]:
        """
        Load ABI and BIN files.

        Returns:
            Tuple[List[Any], str]: The contract ABI and binary.

        Raises:
            FileNotFoundError: If the ABI or BIN files are not found.
        """
        abi_path = f'build/{base_filename}ABI.json'
        bin_path = f'build/{base_filename}BIN.json'

        with open(abi_path, 'r', encoding='utf-8') as abi_file:
            contract_abi = json.load(abi_file)

        with open(bin_path, 'r', encoding='utf-8') as bin_file:
            contract_bin = bin_file.read()

        return contract_abi, contract_bin


    def build_transaction(self) -> dict:
        """
        Build the deployment transaction.

        Returns:
            dict: The transaction dictionary.
        """
        gas_price = self.w3.eth.gas_price
        LOGGER.info("Current gas price: %s gwei", self.w3.from_wei(gas_price, 'gwei'))

        balance = self.w3.eth.get_balance(self.contract_account.address)
        LOGGER.info("ETH Balance: %s ETH", self.w3.from_wei(balance, 'ether'))

        transaction = self.contract.constructor(*self.constructor_args).build_transaction({
            'from': self.contract_account.address,
            'nonce': self.w3.eth.get_transaction_count(self.contract_account.address),
            'gas': 1_500_000,
            'gasPrice': int(gas_price)
        })
        return transaction


    def sign_and_send_transaction(self, transaction: dict) -> str:
        """
        Sign and send the transaction.

        Args:
            transaction (dict): The transaction dictionary.

        Returns:
            str: The transaction hash.
        """

        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.pkey)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        LOGGER.info("tx_hash: %s", tx_hash.hex())
        return tx_hash


    def wait_for_transaction(self, tx_hash: str, max_attempts: int = 50) -> dict:
        """
        Wait for the transaction to be mined and confirmed.

        Args:
            tx_hash (str): The transaction hash.
            max_attempts (int): The maximum number of attempts to wait for confirmation.

        Returns:
            dict: The transaction receipt.

        Raises:
            TimeoutError: If the transaction is not confirmed within the maximum attempts.
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if tx_receipt:
                    LOGGER.info("Transaction confirmed: %s", tx_receipt)
                    return tx_receipt
            except TransactionNotFound:
                LOGGER.info("Attempt %d: Waiting for transaction confirmation...", attempt + 1)

            time.sleep(5)
            attempt += 1

        raise TimeoutError(f"Transaction: {tx_hash.hex()} not confirmed \
                           after {max_attempts} attempts.")

    def deploy(self) -> str:
        """Main method to deploy the contract."""
        LOGGER.info("contract_account.address: %s", self.contract_account.address)
        LOGGER.info("nonce: %d", self.w3.eth.get_transaction_count(self.contract_account.address))

        transaction = self.build_transaction()
        tx_hash = self.sign_and_send_transaction(transaction)
        tx_receipt = self.wait_for_transaction(tx_hash)

        contract_address = tx_receipt.contractAddress
        LOGGER.info("Contract deployed at address: %s", contract_address)

        return contract_address
