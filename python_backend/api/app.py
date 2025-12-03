"""
FastAPI application setup for the WildWeb3 backend.
Registers routes, loads configuration, and performs startup checks.
"""

from fastapi import FastAPI, HTTPException
from services.contract_store import check_tables
from core.logger_config import LOGGER

from api.routes_compile import router as compile_router
from api.routes_deploy import router as deploy_router
from api.routes_metadata import router as metadata_router
from api.routes_inbox import router as inbox_router


def create_app(config: dict) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="WildWeb3",
        description="Web3 Playground",
        openapi_tags=[
            {
                "name": "WildWeb3 REST API",
                "description": "A place to play with Solidity",
            }
        ],
    )

    @app.on_event("startup")
    async def on_startup():
        if not check_tables():
            raise HTTPException(
                status_code=500,
                detail="Table 'contracts' does not exist in the database",
            )

    # Store config in app state
    app.state.config = config

    # Register routes
    app.include_router(compile_router, prefix="/contracts", tags=["Compile"])
    app.include_router(deploy_router, prefix="/contracts", tags=["Deploy"])
    app.include_router(metadata_router, prefix="/contracts", tags=["Metadata"])
    app.include_router(inbox_router, prefix="/inbox", tags=["Inbox"])

    @app.get("/")
    def read_root():
        return {
            "title": app.title,
            "description": app.description,
            "openapi_tags": app.openapi_tags,
        }

    @app.get("/networks")
    def get_available_networks():
        try:
            networks = list(config.get("networks", {}).keys())
            return {"networks": networks}
        except Exception as e:
            LOGGER.error("Failed to fetch networks: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to retrieve networks") from e

    @app.get("/explorer")
    def get_explorer(network: str):
        try:
            networks = config.get("networks", {})

            if network not in networks:
                raise HTTPException(status_code=404, detail=f"Network '{network}' not found")

            explorer_url = networks[network].get("explorer")
            if not explorer_url:
                raise HTTPException(
                    status_code=404,
                    detail=f"No explorer URL configured for network '{network}'",
                )

            return {"explorer_url": explorer_url}

        except HTTPException:
            raise
        except Exception as e:
            LOGGER.error(
                "Unexpected error while fetching explorer URL: %s",
                e,
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail="Unexpected error") from e

    @app.get("/users")
    def get_available_users():
        try:
            users = list(config.get("accounts", {}).keys())
            return {"users": users}
        except Exception as e:
            LOGGER.error("Failed to fetch users: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to retrieve users") from e

    return app
