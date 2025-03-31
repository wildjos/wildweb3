"""
Module: routes_metadata
This module defines the FastAPI routes for handling metadata related to deployed contracts.
It includes a single route for retrieving contract metadata, processing deployment timestamps,
and generating explorer URLs for each contract based on the network configuration.

Routes:
    - GET /metadata: Retrieves metadata for all deployed contracts, including deployment timestamps
      and explorer URLs, and returns the data in JSON format.
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from python_backend.contract_store import get_contracts
from python_backend.deploy_contract import Contract


router = APIRouter()

@router.get("/metadata")
def contracts(req: Request):
    """
    Handles the retrieval and processing of contract metadata.
    This function fetches contract data, formats timestamps, adds explorer URLs 
    based on network configurations, and serializes the data into JSON format 
    for the response.
    Args:
        req (Request): The incoming HTTP request containing application state.
    Returns:
        JSONResponse: A JSON response containing the processed contract metadata.
    Raises:
        HTTPException: If an error occurs during processing, a 500 status code 
        with the error details is returned.
    """

    try:
        config = req.app.state.config

        contract_list = get_contracts()
        for contract in contract_list:
            if isinstance(contract.get("deployment_timestamp"), datetime):
                contract["deployment_timestamp"] = contract["deployment_timestamp"].isoformat()

        networks = config.get("networks", {})
        for contract in contract_list:
            network = contract.get("network")
            contract["explorer_url"] = networks.get(network, {}).get("explorer")

        contract_models = [Contract(**contract) for contract in contract_list]
        return JSONResponse(content={"contracts": [contract.model_dump(mode="json") \
                                                    for contract in contract_models]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
