from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import uuid
import secrets
from . import db
from .agent import chat_with_agent

router = APIRouter()

class InitRequest(BaseModel):
    team_id: str = "TEAM_GUEST"

class ChatRequest(BaseModel):
    session_id: str
    message: str

class RedeemRequest(BaseModel):
    credential: str
    session_id: str = ""

@router.post("/init")
async def init_session():
    session_id = str(uuid.uuid4())
    salt = secrets.token_hex(16)
    nonce = secrets.token_hex(16)
    seed = secrets.token_hex(16)
    db.create_session(session_id, "TEAM_GUEST", salt, nonce, seed)
    return {"session_id": session_id}

@router.post("/chat")
async def chat(req: ChatRequest):
    session = db.get_session(req.session_id)
    if not session:
        return {"response": "Invalid session"}
    
    return chat_with_agent(req.message, req.session_id)

@router.post("/redeem")
async def redeem(req: RedeemRequest):
    if req.credential.startswith("CRED-"):
        from shared.config import settings
        return {"flag": settings.FINAL_FLAG}
    raise HTTPException(status_code=400, detail="Invalid credential")
