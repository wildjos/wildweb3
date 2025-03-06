#!/usr/bin/python3

from fastapi import FastAPI
from compile import compile
from deploy import deploy




tags_metadata = [
    {
        "name": "WildWeb3 REST API",
        "description": "A place to play with Solidity",
    },
]


app = FastAPI(
    title="WildWeb3",
    description="Web3 Playground",
    openapi_tags=tags_metadata,
)

@app.get("/")
def read_root():
    return{
        "title": app.title,
        "description": app.description,
        "openapi_tags": app.openapi_tags,
    }

@app.get("/compile")
def compile_contract():
    # Logic to compile a Solidity contract
    return {"message": "Contract compiled"}

@app.post("/deploy")
def deploy_contract():
    # Logic to deploy contract
    return {"contract_address": "0x123..."}

@app.post("/interact")
def interact_contract():
    # Logic to call smart contract functions
    return {"status": "Success"}
