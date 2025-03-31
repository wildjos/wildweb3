"""
routes_inbox.py

This module defines API routes for a FastAPI application. It includes endpoints for retrieving
messages and counters, updating messages, and performing basic mathematical operations.

Routes:
- GET /message: Retrieve a stored message.
- GET /counter: Retrieve a stored counter value.
- PUT /update: Update the stored message.
- POST /maths: Perform basic mathematical operations.
"""
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()

# GET: Retrieve stored message (no change to server state)
@router.get("/message")
def get_message():
    return {"message": "TODO"}

# GET: Retrieve stored counter value (no change to server state)
@router.get("/counter")
def get_counter():
    return {"count": 1}

# PUT: Update the stored message (modifies server state)
class UpdateMessageRequest(BaseModel):
    message: str

@router.put("/update")
def update_message(request: UpdateMessageRequest):
    return {"success": True, "updated_message": request.message}

# POST: Perform calculations (operation depends on parameters but does not modify server)
class MathRequest(BaseModel):
    a: int
    b: int

@router.post("/maths")
def do_maths(request: MathRequest):
    return {
        "sum": request.a + request.b,
        "diff": request.a - request.b,
        "product": request.a * request.b,
        "is_zero": request.a == 0
    }
