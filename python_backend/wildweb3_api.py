'''
from fastapi import FastAPI, HTTPException
WildWeb3 API Module.

This module defines the FastAPI application for the WildWeb3 project, 
including its configuration, startup events, and route registration.
'''
from fastapi import FastAPI, HTTPException
from python_backend.contract_store import check_tables
from python_backend.logger_config import LOGGER
from python_backend.routes_compile import router as compile_router
from python_backend.routes_deploy import router as deploy_router
from python_backend.routes_metadata import router as metadata_router
from python_backend.routes_inbox import router as inbox_router


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


    return app
