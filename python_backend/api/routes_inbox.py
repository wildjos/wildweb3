"""
routes_inbox.py

Inbox contract routes for retrieving messages and counters,
updating a message, and performing basic math operations.
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services.inbox_contract import InboxContract
from core.config import get_updated_config, InvalidNetworkException

router = APIRouter()


@router.get("/message")
def get_message(
    request: Request,
    network: str,
    contract_address: str,
    contract_name: str,
):
    """Fetch a stored message from a contract."""
    try:
        config = request.app.state.config
        updated_config = get_updated_config(config, network)

        contract = InboxContract(
            contract_address=contract_address,
            contract_name=contract_name,
            user=None,
            config=updated_config,
        )

        return {"message": contract.get_message()}

    except InvalidNetworkException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/counter")
def get_counter(
    request: Request,
    network: str,
    contract_address: str,
    contract_name: str,
):
    """Fetch a stored counter value from a contract."""
    try:
        config = request.app.state.config
        updated_config = get_updated_config(config, network)

        contract = InboxContract(
            contract_address=contract_address,
            contract_name=contract_name,
            user=None,
            config=updated_config,
        )

        return {"count": contract.get_counter()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


class UpdateMessageRequest(BaseModel):
    """Payload for updating a message on a contract."""
    message: str
    network: str
    contract_name: str
    contract_address: str
    user: str


@router.put("/update")
def update_message(request: Request, update_data: UpdateMessageRequest):
    """Update a stored message on a contract."""
    try:
        config = request.app.state.config
        updated_config = get_updated_config(config, update_data.network)

        contract = InboxContract(
            contract_address=update_data.contract_address,
            contract_name=update_data.contract_name,
            user=update_data.user,
            config=updated_config,
        )

        tx_hash = contract.update_message(update_data.message)
        return {"success": True, "tx_hash": tx_hash}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


class MathRequest(BaseModel):
    """Payload for math operations via a contract."""
    a: int
    b: int
    network: str
    contract_name: str
    contract_address: str


@router.post("/maths")
def do_maths(request: Request, math_data: MathRequest):
    """Perform math operations using the contract."""
    try:
        config = request.app.state.config
        updated_config = get_updated_config(config, math_data.network)

        contract = InboxContract(
            contract_address=math_data.contract_address,
            contract_name=math_data.contract_name,
            user=None,
            config=updated_config,
        )

        return contract.do_math(math_data.a, math_data.b)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
