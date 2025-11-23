"""
routes_inbox.py

This module defines API routes for a FastAPI application. It includes endpoints for retrieving
messages and counters, updating messages, and performing basic mathematical operations.

Routes:
- GET /message: Retrieve a stored message.
- GET /counter: Retrieve a stored counter value.
- PUT /update: Update the stored message.
- POST /maths: Perform basic mathematical operations.
"""
from pydantic import BaseModel
from fastapi import APIRouter, Query, Request, HTTPException
from services.inbox_contract import InboxContract
from core.config import get_updated_config, InvalidNetworkException

router = APIRouter()

# GET: Retrieve stored message
@router.get("/message")
def get_message(request: Request, network: str = Query(...), \
                contract_address: str = Query(...), \
                contract_name: str = Query(...)):
    """
    Fetches a message from the specified contract on the given network.
    """
    try:
        config = request.app.state.config
        updated_config = get_updated_config(config, network)

        contract = InboxContract(contract_address=contract_address, \
                                 contract_name = contract_name,
                                 user=None, config=updated_config)

        message = contract.get_message()
        return {"message": message}
    except InvalidNetworkException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# GET: Retrieve stored counter value
@router.get("/counter")
def get_counter(request: Request, network: str = Query(...), \
                contract_address: str = Query(...), \
                contract_name: str = Query(...)):
    """
    Retrieve the counter value from a specified smart contract on a given network.
    """
    try:
        config = request.app.state.config
        updated_config = get_updated_config(config, network)

        contract = InboxContract(contract_address=contract_address,
                                 contract_name = contract_name,
                                 user=None, config=updated_config)
        counter = contract.get_counter()
        return {"count": counter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# PUT: Update the stored message
class UpdateMessageRequest(BaseModel):
    """Schema for updating a message request with contract and user details."""
    message: str
    network: str
    contract_name: str
    contract_address: str
    user_account: str

@router.put("/update")
def update_message(request: Request, update_data: UpdateMessageRequest):
    """
    Updates a message on the blockchain using the provided update data.
    """
    try:
        config = request.app.state.config
        updated_config = get_updated_config(config, update_data.network)

        contract = InboxContract(contract_address=update_data.contract_address,
                                 contract_name = update_data.contract_name,
                                 user=update_data.user_account,
                                 config=updated_config)

        tx_hash = contract.update_message(update_data.message)
        return {"success": True, "tx_hash": tx_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# POST: Perform calculations via the smart contract
class MathRequest(BaseModel):
    """Represents a mathematical operation request with contract details and network information."""
    a: int
    b: int
    network: str
    contract_name: str
    contract_address: str

@router.post("/maths")
def do_maths(request: Request, math_data: MathRequest):
    """
    Handles a math operation request by interacting with a smart contract and returns the result.
    """
    try:
        print("DEBUG: in do_maths")
        config = request.app.state.config
        print(f"config: {config}")
        updated_config = get_updated_config(config, math_data.network)
        print(f"updated_config: {updated_config}")

        # contract = InboxContract(math_data.network, math_data.contract_address, config)
        contract = InboxContract(contract_address=math_data.contract_address,
                                 contract_name = math_data.contract_name,
                                 user=None, config=updated_config)

        result = contract.do_math(math_data.a, math_data.b)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
