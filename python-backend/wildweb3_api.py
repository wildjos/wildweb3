#!/usr/bin/python3
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from compile import compile
from deploy import deploy
from pydantic import BaseModel


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

@app.post("/compile")
async def compile_solidity(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    # Save the file
    with open(file_location, "wb") as f:
        f.write(await file.read())


    # Logic to compile a Solidity contract
    compile(file_location)
    return {"message": "Contract compiled"}


class DeployRequest(BaseModel):
    contract_name: str
    constructor_args: list

@app.post("/deploy")
def deploy_contract(request: DeployRequest):
    try:
        # Call the deploy function with the base filename
        contract_address = deploy(request.contract_name, request.constructor_args)
        return {"contract_address": contract_address}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interact")
def interact_contract():
    # Logic to call smart contract functions
    return {"status": "Success"}


@app.get("/compiled_contracts")
def get_compiled_contracts():
    compiled_contracts = []
    build_dir = "build"
    if os.path.exists(build_dir):
        for filename in os.listdir(build_dir):
            if filename.endswith("ABI.json"):
                contract_name = filename.replace("ABI.json", "")
                compiled_contracts.append({"name": contract_name})
    return JSONResponse(content=compiled_contracts)