'''
from fastapi import FastAPI, HTTPException
WildWeb3 API Module.

This module defines the FastAPI application for the WildWeb3 project,
including its configuration, startup events, and route registration.
'''
from fastapi import FastAPI, HTTPException
from services.contract_store import check_tables
from core.logger_config import LOGGER
from api.routes_compile import router as compile_router
from api.routes_deploy import router as deploy_router
from api.routes_metadata import router as metadata_router
from api.routes_inbox import router as inbox_router


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
            raise HTTPException(status_code=500, \
                                detail="Table 'contracts' does not exist in the database")

    # # Register all API routes

    # Store config in app state
    app.state.config = config

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
            # Access the networks from the config
            networks = config.get("networks", {})

            # Check if the network exists
            if network not in networks:
                raise HTTPException(status_code=404, detail=f"Network '{network}' not found")

            # Get the explorer URL for the network
            explorer_url = networks[network].get("explorer")
            if not explorer_url:
                raise HTTPException(status_code=404, \
                                    detail=f"Explorer URL not found for network '{network}'")

            return {"explorer_url": explorer_url}

        except HTTPException as e:
            LOGGER.error("HTTP error occurred: %s", {e.detail})
            raise e
        except Exception as e:
            LOGGER.error("Unexpected error occurred while fetching explorer URL: %e", e, \
                         exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


    @app.get("/users")
    def get_available_users():
        print("DEBUG: in /users")
        try:
            users = list(config.get("accounts", {}).keys())
            print(f"DEBUG: users = {users}")
            return {"users": users}
        except Exception as e:
            LOGGER.error("Failed to fetch users: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to retrieve users") from e

    return app
