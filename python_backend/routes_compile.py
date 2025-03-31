"""
Module: routes_compile

This module provides API endpoints for uploading and compiling Solidity smart contracts 
using FastAPI. It includes functionality to upload Solidity files, compile them, and 
retrieve a list of compiled contracts.

Routes:
- GET /compiled_contracts: Retrieves a list of compiled Solidity contracts.
- POST /compile: Uploads a Solidity file and triggers its compilation.

Constants:
- UPLOADS_PATH: Directory where uploaded files are temporarily stored.

Functions:
- compile_solidity_function(file_location): Placeholder function for Solidity compilation logic.
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from python_backend.compile_solidity import compile_solidity as compile_solidity_function
from python_backend.constants import UPLOADS_PATH

router = APIRouter()


@router.post("/compile")
async def compile_solidity(file: UploadFile = File(...)):
    """
    Asynchronously compiles a Solidity contract file uploaded by the user.
    Args:
        file (UploadFile): The uploaded Solidity file to be compiled.
    Returns:
        dict: A message indicating the compilation status.
    """

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(UPLOADS_PATH, unique_filename)

    with open(file_location, "wb") as f:
        f.write(await file.read())

    compile_solidity_function(file_location)
    return {"message": "Contract compiled"}


@router.get("/compiled_contracts")
def get_compiled_contracts():
    """
    Retrieves a list of compiled contract names from the build directory.
    Returns:
        JSONResponse: A response containing a list of contract names with their metadata.
    """

    compiled_contracts = []
    build_dir = "build"
    if os.path.exists(build_dir):
        for filename in os.listdir(build_dir):
            if filename.endswith("ABI.json"):
                contract_name = filename.replace("ABI.json", "")
                compiled_contracts.append({"name": contract_name})
    return JSONResponse(content=compiled_contracts)
