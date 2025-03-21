"""
Module for deploying Solidity contracts.
"""

import time
import json
from datetime import datetime
from web3.exceptions import TransactionNotFound
from web3.contract import Contract as Web3Contract
from python_backend.models import Contract
from python_backend.contract_store import store_contract_info
from python_backend.ethereum_account import EthereumAccount
from python_backend.logger_config import LOGGER


class ContractDeployer:
    """
    Class for deploying Solidity contracts.
    """

    def __init__(self, base_filename: str, user: str, constructor_args: list, config: dict):
        """
        Initialise the ContractDeployer.

        Args:
            base_filename (str): The base filename of the contract's ABI and BIN files.
            user (str): The user deploying the contract.
            constructor_args (List[Any]): The arguments for the contract's constructor.
            config (dict): The configuration dictionary.
        """
        self.config = config
        self.contract_name = base_filename
        self.user = user
        self.constructor_args = constructor_args

        # EthereumAccount for account management
        self.eth_account = EthereumAccount(user, config)
        self.contract = self.load_contract(base_filename)


    def load_contract(self, base_filename: str) -> Web3Contract:
        """
        Load ABI and BIN files.

        Returns:
            Web3.eth.Contract: The contract instance.

        Raises:
            FileNotFoundError: If the ABI or BIN files are not found.
        """
        abi_path = f'build/{base_filename}ABI.json'
        bin_path = f'build/{base_filename}BIN.json'

        with open(abi_path, 'r', encoding='utf-8') as abi_file:
            contract_abi = json.load(abi_file)

        with open(bin_path, 'r', encoding='utf-8') as bin_file:
            contract_bin = bin_file.read()

        return self.eth_account.w3.eth.contract(abi=contract_abi, bytecode=contract_bin)


    def build_transaction(self) -> dict:
        """
        Build the deployment transaction.

        Returns:
            dict: The transaction dictionary.
        """
        gas_price = self.eth_account.get_gas_price()
        LOGGER.info("Current gas price: %s gwei", self.eth_account.from_wei(gas_price, 'gwei'))

        balance = self.eth_account.get_balance()
        LOGGER.info("ETH Balance: %s ETH", self.eth_account.from_wei(balance, 'ether'))

        estimated_gas = self.contract.constructor(*self.constructor_args).estimate_gas({
            'from': self.eth_account.account.address
        })

        # Total gas cost in wei
        gas_cost = estimated_gas * gas_price
        LOGGER.info("Estimated gas cost: %s ETH", self.eth_account.from_wei(gas_cost, 'ether'))

        # Ensure the account has enough balance
        if balance < gas_cost:
            raise ValueError(
                f"Insufficient balance ({self.eth_account.from_wei(balance, 'ether')} ETH) "
                f"to cover estimated gas cost ({self.eth_account.from_wei(gas_cost, 'ether')} ETH)."
            )

        transaction = self.contract.constructor(*self.constructor_args).build_transaction({
            'from': self.eth_account.account.address,
            'nonce': self.eth_account.get_nonce(),
            'gas': estimated_gas,
            # 'gas': 1_500_000,
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
        signed_txn = self.eth_account.sign_transaction(transaction)
        tx_hash = self.eth_account.send_transaction(signed_txn)
        LOGGER.info("Transaction Hash: %s", tx_hash)
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
                tx_receipt = self.eth_account.w3.eth.get_transaction_receipt(tx_hash)
                if tx_receipt:
                    LOGGER.info("Transaction confirmed: %s", tx_receipt)
                    return tx_receipt
            except TransactionNotFound:
                LOGGER.info("Attempt %d: Waiting for transaction confirmation...", attempt + 1)

            # Detect stuck transactions and reattempt with a higher gas price
            if attempt % 10 == 0:  # Every 10 attempts, check if it's stuck
                pending_tx = dict(self.eth_account.w3.eth.get_transaction(tx_hash))
                current_gas_price = self.eth_account.get_gas_price()

                if pending_tx["gasPrice"] < current_gas_price:
                    LOGGER.warning("Transaction is likely stuck. \
                                   Resubmitting with higher gas price...")
                    new_tx = pending_tx.copy()
                    new_tx["gasPrice"] = int(current_gas_price * 1.2)  # Increase gas price
                    signed_tx = self.eth_account.sign_transaction(new_tx)
                    tx_hash = self.eth_account.send_transaction(signed_tx)
                    LOGGER.info("Replaced transaction with new hash: %s", tx_hash.hex())

            time.sleep(5)
            attempt += 1

        raise TimeoutError(f"Transaction {tx_hash} not confirmed after {max_attempts} attempts.")


    def deploy(self) -> str:
        """
        Deploy the contract and store the deployment information.

        Returns:
            str: The address of the deployed contract.

        Raises:
            RuntimeError: If storing the contract information in the database fails.
        """
        LOGGER.info("Deploying contract from address: %s", self.eth_account.account.address)

        transaction = self.build_transaction()
        tx_hash = self.sign_and_send_transaction(transaction)
        tx_receipt = self.wait_for_transaction(tx_hash)

        contract_address = tx_receipt.contractAddress
        LOGGER.info("Contract deployed at address: %s", contract_address)

        deployment_tx_hash = tx_receipt['transactionHash'].hex()

        # Prepare the contract information using the Contract class
        info = Contract(
            name=self.contract_name,
            user_name=self.user,
            deployer_address=self.eth_account.account.address,
            contract_address=contract_address,
            network=self.config["network"]["name"],
            deployment_tx_hash=deployment_tx_hash,
            deployment_timestamp=datetime.now()
        )

        LOGGER.debug("Deployment info: %s", info)

        # Store contract info in DB, and let exceptions propagate
        try:
            store_contract_info(info)
        except RuntimeError as e:
            LOGGER.error("Failed to store contract info: %s", e)
            raise

        return contract_address
