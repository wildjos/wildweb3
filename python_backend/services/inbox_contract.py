'''
Module: inbox_contract

This module provides the `InboxContract` class, which facilitates interactions
with a deployed Solidity smart contract named "Inbox". The class includes methods
to fetch and update the contract's stored message, retrieve a counter value, and
perform mathematical operations using the contract's functions.
'''

import json
from web3.contract import Contract as Web3Contract
from web3.exceptions import ContractLogicError, TransactionNotFound
from services.ethereum_account import EthereumAccount
from core.logger_config import LOGGER
from core.web3_connector import Web3Connector

class InboxContract:
    """
    Handles interactions with the Inbox Solidity contract.
    """

    def __init__(self, contract_address: str, contract_name: str,
                 user: str, config: dict):
        """
        Initializes the InboxContract class.

        Args:
            contract_address (str): The deployed contract address.
            user (str): The user interacting with the contract.
            config (dict): The configuration dictionary.
        """
        print(f"DEBUG: --init--: config = {config}")
        self.config = config
        self.contract_address = contract_address

        if user:
            self.eth_account = EthereumAccount(user, config)
            self.w3 = self.eth_account.w3
        else:
            self.eth_account = None
            self.w3 = Web3Connector(self.config["network"]).get_web3()
            self.account = None

        self.contract = self.load_contract(contract_name)

    def load_contract(self, contract_name: str) -> Web3Contract:
        """
        Load the deployed Inbox contract using its ABI.

        Returns:
            Web3.eth.Contract: The contract instance.
        """
        abi_path = "build/" + contract_name + "ABI.json"

        with open(abi_path, "r", encoding="utf-8") as abi_file:
            contract_abi = json.load(abi_file)

        return self.w3.eth.contract(
            address=self.contract_address, abi=contract_abi
        )

    def get_message(self) -> str:
        """
        Fetch the stored message from the contract.

        Returns:
            str: The stored message.
        """
        try:
            return self.contract.functions.message().call()
        except ContractLogicError as e:
            LOGGER.error("Failed to fetch message: %s", str(e))
            return "Error fetching message"
        except Exception as e: # pylint: disable=broad-exception-caught
            LOGGER.error("Unexpected error while fetching message: %s", str(e))
            return "Error fetching message"

    def get_counter(self) -> int:
        """
        Fetch the counter value from the contract.

        Returns:
            int: The counter value.
        """
        try:
            return self.contract.functions.counter().call()
        except ContractLogicError as e:
            LOGGER.error("Failed to fetch counter: %s", str(e))
            return -1
        except Exception as e: # pylint: disable=broad-exception-caught
            LOGGER.error("Unexpected error while fetching message: %s", str(e))
            return -1

    def update_message(self, new_message: str) -> str:
        """
        Update the message in the contract.

        Args:
            new_message (str): The new message to store.

        Returns:
            str: Transaction hash of the update.
        """
        try:
            nonce = self.eth_account.get_nonce()
            gas_price = self.eth_account.get_gas_price()
            gas_limit = 150000

            txn = self.contract.functions.setMessage(new_message).build_transaction({
                "from": self.eth_account.account.address,
                "nonce": nonce,
                "gas": gas_limit,
                "gasPrice": gas_price,
            })

            signed_txn = self.eth_account.sign_transaction(txn)
            tx_hash = self.eth_account.send_transaction(signed_txn)

            LOGGER.info("Message update transaction sent: %s", tx_hash)
            return tx_hash
        except TransactionNotFound as e:
            LOGGER.error("Transaction not found: %s", str(e))
            return "Error updating message"
        except ValueError as e:
            LOGGER.error("Invalid transaction parameters: %s", str(e))
            return "Error updating message"
        except Exception as e: # pylint: disable=broad-exception-caught
            LOGGER.error("Unexpected error while updating message: %s", str(e))
            return "Error updating message"

    def do_math(self, a: int, b: int) -> dict:
        """
        Calls the smart contract function to perform math operations.

        Args:
            a (int): First number.
            b (int): Second number.

        Returns:
            dict: A dictionary containing sum, difference, product, and is_zero.
        """
        try:
            result = self.contract.functions.doMath(a, b).call()
            return {
                "sum": result[0],
                "diff": result[1],
                "product": result[2],
                "is_zero": result[3],
            }
        except ContractLogicError as e:
            LOGGER.error("Math operation failed: %s", str(e))
            return {"error": "Math operation failed"}
        except ValueError as e:
            LOGGER.error("Invalid input for math operation: %s", str(e))
            return {"error": "Invalid input"}
        except Exception as e: # pylint: disable=broad-exception-caught
            LOGGER.error("Unexpected error during math operation: %s", str(e))
            return {"error": "Math operation failed"}
