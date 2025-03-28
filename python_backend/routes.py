'''
"""
This module defines the API routes for a FastAPI application that interacts with 
Solidity smart contracts. It includes endpoints for compiling, deploying, and 
interacting with contracts, as well as retrieving metadata and available networks.

Functions:
    register_routes(app: FastAPI, config: dict):
        Registers all API endpoints to the FastAPI application.

    read_root():
        Handles the root endpoint and provides basic application metadata.

    compile_solidity(file: UploadFile):
        Compiles a Solidity smart contract file uploaded by the user.

    get_available_networks():
        Retrieves a list of available blockchain networks from the configuration.

    deploy_contract(request: DeployRequest):
        Deploys a compiled smart contract to a specified blockchain network.

    interact_contract():
        Placeholder endpoint for interacting with deployed smart contracts.

    get_compiled_contracts():
        Retrieves a list of compiled contracts available in the build directory.

    contracts():
        Retrieves metadata for deployed contracts, including deployment timestamps 
        and network explorer URLs.
"""
'''
import os
import uuid
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from python_backend.compile_solidity import compile_solidity as compile_solidity_function
from python_backend.deploy_contract import ContractDeployer, Contract
from python_backend.constants import UPLOADS_PATH
from python_backend.contract_store import get_contracts
from python_backend.logger_config import LOGGER


def register_routes(app: FastAPI, config: dict):
    """Register all API endpoints to the FastAPI application."""

    @app.get("/")
    def read_root():
        return {
            "title": app.title,
            "description": app.description,
            "openapi_tags": app.openapi_tags,
        }

    @app.post("/compile")
    async def compile_solidity(file: UploadFile = File(...)):
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_location = os.path.join(UPLOADS_PATH, unique_filename)

        with open(file_location, "wb") as f:
            f.write(await file.read())

        compile_solidity_function(file_location)
        return {"message": "Contract compiled"}


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


    @app.get("/networks")
    def get_available_networks():
        try:
            networks = list(config.get("networks", {}).keys())
            return {"networks": networks}
        except Exception as e:
            LOGGER.error("Failed to fetch networks: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to retrieve networks") from e

    @app.post("/deploy")
    def deploy_contract(request: DeployRequest):
        try:
            networks = config.get("networks", {})
            network_name = request.network_name

            if network_name not in networks:
                raise HTTPException(status_code=400, detail=f"Invalid network: {network_name}")

            updated_config = config.copy()
            updated_config["network"] = networks[network_name]

            deployer = ContractDeployer(
                base_filename=request.contract_name,
                user=request.user,
                constructor_args=request.constructor_args,
                config=updated_config,
            )

            contract_address = deployer.deploy()
            return {"contract_address": contract_address}
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        except Exception as e:
            LOGGER.error("Deployment failed: %s", e, exc_info=True)
            raise HTTPException(status_code=500, \
                                detail="An unexpected error occurred: " + str(e)) from e

    @app.post("/interact")
    def interact_contract():
        return {"status": "Success"}

    @app.get("/compiled_contracts")
    def get_compiled_contracts():
        compiled_contracts = []
        build_dir = "build"
        if os.path.exists(build_dir):
            for filename in os.listdir(build_dir):
                if filename.endswith("ABI.json"):
                    contract_name = filename.replace("ABI.json", "")
                    compiled_contracts.append({"name": contract_name})
        return JSONResponse(content=compiled_contracts)

    @app.get("/metadata/contracts")
    def contracts():
        try:
            contracts = get_contracts()
            for contract in contracts:
                if isinstance(contract.get("deployment_timestamp"), datetime):
                    contract["deployment_timestamp"] = contract["deployment_timestamp"].isoformat()

            networks = config.get("networks", {})
            for contract in contracts:
                network = contract.get("network")
                contract["explorer_url"] = networks.get(network, {}).get("explorer")

            contract_models = [Contract(**contract) for contract in contracts]
            return JSONResponse(content={"contracts": [contract.model_dump(mode="json") \
                                                       for contract in contract_models]})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
