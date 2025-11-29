"""
Deployment routes for compiling and deploying smart contracts.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from services.deploy_contract import ContractDeployer
from core.logger_config import LOGGER
from core.config import get_updated_config, InvalidNetworkException

router = APIRouter()


class DeployRequest(BaseModel):
    """Payload for deploying a smart contract."""
    network_name: str
    contract_name: str
    user: str
    constructor_args: list = Field(default_factory=list)


@router.post("/deploy")
def deploy_contract(req: Request, data: DeployRequest):
    """Deploy a smart contract to the selected network."""
    try:
        config = req.app.state.config
        updated_config = get_updated_config(config, data.network_name)

        deployer = ContractDeployer(
            base_filename=data.contract_name,
            user=data.user,
            constructor_args=data.constructor_args,
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
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {e}"
        ) from e
