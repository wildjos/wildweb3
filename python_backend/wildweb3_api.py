#!/usr/bin/python3
"""
WildWeb3 REST API module.
"""

import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from python_backend.compile_solidity import compile_solidity as compile_solidity_function
from python_backend.deploy_contract import ContractDeployer



UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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


    @app.post("/compile")
    async def compile_solidity(file: UploadFile = File(...)):
        """
        Endpoint to compile a Solidity contract.
        """
        file_location = os.path.join(UPLOAD_DIR, file.filename)

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
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e


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

    return app
