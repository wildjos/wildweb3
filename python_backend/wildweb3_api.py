#!/usr/bin/python3
"""
WildWeb3 REST API module.
"""

import os
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from python_backend.compile_solidity import compile_solidity as compile_solidity_function
from python_backend.deploy_contract import ContractDeployer, Contract
from python_backend.constants import UPLOADS_PATH
from python_backend.contract_store import check_tables, get_contracts
from python_backend.logger_config import LOGGER


tags_metadata = [
    {
        "name": "WildWeb3 REST API",
        "description": "A place to play with Solidity",
    },
]



def create_app(config: dict) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    app = FastAPI(
        title="WildWeb3",
        description="Web3 Playground",
        openapi_tags=tags_metadata,
    )

    @app.on_event("startup")
    async def on_startup():

        table_exists = check_tables()
        if not table_exists:
            raise HTTPException(status_code=500, detail=\
                                "Table 'contracts' does not exist in the database")



    @app.get("/")
    def read_root():
        """
        Root endpoint returning API metadata.
        """
        return{
            "title": app.title,
            "description": app.description,
            "openapi_tags": app.openapi_tags,
        }

    # Compilation, Deployment & Interaction Endpoints
    #

    @app.post("/compile")
    async def compile_solidity(file: UploadFile = File(...)):
        """
        Endpoint to compile a Solidity contract.
        """
        file_location = os.path.join(UPLOADS_PATH, file.filename)

        # Save the file
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Logic to compile a Solidity contract
        compile_solidity_function(file_location)
        return {"message": "Contract compiled"}


    class DeployRequest(BaseModel):
        """
        Request model for deploying a contract.
        """
        contract_name: str
        user: str
        constructor_args: list


    @app.post("/deploy")
    def deploy_contract(request: DeployRequest):
        """
        Endpoint to deploy a Solidity contract.
        """
        try:
            # Create an instance of ContractDeployer
            deployer = ContractDeployer(\
                base_filename=request.contract_name, \
                user=request.user, \
                constructor_args=request.constructor_args,
                config=config)

            # Call the deploy function with the base filename
            contract_address = deployer.deploy()

            return {"contract_address": contract_address}
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        except Exception as e:
            LOGGER.error("Deployment failed: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail=\
                                "An unexpected error occurred: " + str(e)) from e


    @app.post("/interact")
    def interact_contract():
        """
        Endpoint to interact with a deployed contract.
        """
        # Logic to call smart contract functions
        return {"status": "Success"}


    @app.get("/compiled_contracts")
    def get_compiled_contracts():
        """
        Endpoint to get a list of compiled contracts.
        """
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
        """
        Endpoint to retrieve all contract information.
        """
        try:
            contracts = get_contracts()
            print(contracts)

            # Convert datetime fields before creating Contract objects
            for contract in contracts:
                if isinstance(contract.get("deployment_timestamp"), datetime):
                    contract["deployment_timestamp"] = contract["deployment_timestamp"].isoformat()

            contract_models = [Contract(**contract) for contract in contracts]

            return JSONResponse(
                content={"contracts": [contract.model_dump(mode="json") \
                                       for contract in contract_models]}
    )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    return app
