'''
from fastapi import FastAPI, HTTPException
WildWeb3 API Module.

This module defines the FastAPI application for the WildWeb3 project, 
including its configuration, startup events, and route registration.
'''
from fastapi import FastAPI, HTTPException
from python_backend.contract_store import check_tables
from python_backend.routes import register_routes


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

    # Register all API routes
    register_routes(app, config)

    return app
