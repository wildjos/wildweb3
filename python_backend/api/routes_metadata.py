"""
Routes for returning metadata about deployed contracts.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from services.contract_store import get_contracts
from api.models import Contract

router = APIRouter()


@router.get("/metadata")
def list_contracts(req: Request):
    """Return metadata for all deployed contracts."""
    try:
        config = req.app.state.config
        networks = config.get("networks", {})

        raw_contracts = get_contracts()
        processed = []

        for c in raw_contracts:
            # Format timestamp
            ts = c.get("deployment_timestamp")
            if isinstance(ts, datetime):
                c["deployment_timestamp"] = ts.isoformat()

            # Add explorer URL if available
            network = c.get("network")
            c["explorer_url"] = networks.get(network, {}).get("explorer")

            processed.append(Contract(**c))

        return {"contracts": [p.model_dump(mode="json") for p in processed]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
