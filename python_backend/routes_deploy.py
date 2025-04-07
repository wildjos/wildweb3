"""
This module defines the API routes for a FastAPI application that facilitates 
interaction with Solidity smart contracts. It provides endpoints for deploying 
contracts, retrieving metadata, and managing blockchain networks.

Functions:
    register_routes(app: FastAPI, config: dict):
        Registers deployment-related API endpoints to the FastAPI application.

    deploy_contract(request: DeployRequest):
        Deploys a smart contract to a specified blockchain network, using the 
        provided configuration and constructor arguments.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from python_backend.deploy_contract import ContractDeployer
from python_backend.logger_config import LOGGER
from python_backend.config import get_updated_config, InvalidNetworkException


router = APIRouter()


class DeployRequest(BaseModel):
    """
    DeployRequest is a data model representing a request to deploy a smart contract.
    Attributes:
        network_name (str): The name of the blockchain where the contract will be deployed.
        contract_name (str): The name of the smart contract to be deployed.
        user (str): The identifier of the user initiating the deployment.
        constructor_args (list): A list of arguments passed to the smart contract's constructor.
    """

    network_name: str
    contract_name: str
    user: str
    constructor_args: list


@router.post("/deploy")
def deploy_contract(request: DeployRequest, req: Request):
    """
    Deploys a smart contract to the specified blockchain network.
    Args:
        request (DeployRequest): The deployment request containing the contract name,
                                 user information, constructor arguments, and network name.
        req (Request): The HTTP request object, used to access application state and configuration.
    Returns:
        dict: A dictionary containing the deployed contract's address.
    Raises:
        HTTPException: If the specified network is invalid or if a runtime error occurs.
    """

    try:
        config = req.app.state.config
        updated_config = get_updated_config(config, request.network_name)

        deployer = ContractDeployer(
            base_filename=request.contract_name,
            user=request.user,
            constructor_args=request.constructor_args,
            config=updated_config,
        )

        contract_address = deployer.deploy()
        return {"contract_address": contract_address}
    except InvalidNetworkException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        LOGGER.error("Deployment failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, \
                            detail="An unexpected error occurred: " + str(e)) from e
