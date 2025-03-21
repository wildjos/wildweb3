"""
This module defines the data models used in the application.

Classes:
    Contract: A Pydantic model representing a smart contract with various attributes.
"""

from datetime import datetime
from pydantic import BaseModel


class Contract(BaseModel):
    """
    Represents a smart contract deployment.
    Attributes:
        contract_name (str): The name of the contract.
        deployer_name (str, optional): The name of the user who deployed the contract. \
            Defaults to None.
        deployer_address (str, optional): The address of the deployer. Defaults to None.
        contract_address (str, optional): The address of the deployed contract. Defaults to None.
        network (str): The network on which the contract is deployed, e.g. 'sepolia'.
        deployment_tx_hash (str): The transaction hash of the deployment.
        deployment_timestamp (datetime): The timestamp of the deployment.
    """

    contract_name: str
    deployer_name: str = None
    deployer_address: str = None
    contract_address: str = None
    network: str
    deployment_tx_hash: str
    deployment_timestamp: datetime
