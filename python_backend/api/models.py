"""
Pydantic models used by the backend.
"""

from datetime import datetime
from pydantic import BaseModel


class Contract(BaseModel):
    """Represents a deployed smart contract and its metadata."""

    contract_name: str
    network: str
    deployment_tx_hash: str
    deployment_timestamp: datetime

    deployer_name: str | None = None
    deployer_address: str | None = None
    contract_address: str | None = None
    explorer_url: str | None = None
