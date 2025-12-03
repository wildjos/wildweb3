"""
Routes for uploading and compiling Solidity contracts.
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File
from services.compile_solidity import compile_solidity as compile_solidity_function
from core.constants import UPLOADS_PATH
from core.logger_config import LOGGER

router = APIRouter()


@router.post("/compile")
async def compile_solidity(file: UploadFile = File(...)):
    """Upload and compile a Solidity contract."""
    try:
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_location = os.path.join(UPLOADS_PATH, unique_filename)

        # Save uploaded file
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Compile contract
        compile_solidity_function(file_location)

        return {
            "success": True,
            "message": "Contract compiled successfully",
            "filename": unique_filename,
        }

    except FileNotFoundError as e:
        LOGGER.error("File not found: %s", e, exc_info=True)
        return {"success": False, "message": f"File not found: {e}"}

    except OSError as e:
        LOGGER.error("OS error: %s", e, exc_info=True)
        return {"success": False, "message": f"OS error: {e}"}

    except ValueError as e:
        LOGGER.error("Compilation value error: %s", e, exc_info=True)
        return {"success": False, "message": f"Value error: {e}"}

    except Exception as e:  # pylint: disable=broad-exception-caught
        LOGGER.error("Unexpected error: %s", e, exc_info=True)
        return {
            "success": False,
            "message": "Unexpected error during compilation.",
        }


@router.get("/compiled_contracts")
def get_compiled_contracts():
    """Return a list of compiled contracts in the build directory."""
    build_dir = "build"
    compiled_contracts = []

    if os.path.exists(build_dir):
        for filename in os.listdir(build_dir):
            if filename.endswith("ABI.json"):
                name = filename.replace("ABI.json", "")
                compiled_contracts.append({"name": name})

    return compiled_contracts
