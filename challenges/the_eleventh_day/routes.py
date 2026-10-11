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
    import hmac as hmac_lib
    # session_id is required for validation
    if not req.session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    session = db.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session")

    # Reconstruct what the real credential for this session should be
    expected_key = f"FINAL_{req.session_id.replace('-', '')[:16].upper()}"
    expected_credential = f"CRED-{expected_key}"

    # Use constant-time comparison to prevent timing attacks
    if hmac_lib.compare_digest(req.credential.strip(), expected_credential):
        # Also verify Phase 1 + Phase 2 were actually completed
        phase1_done = session.get("first_story_complete", False)
        phase2_done = session.get("story_b_complete", False) or "PHASE2_COMPLETE" in session.get("story_b_sequence", [])
        if phase1_done and phase2_done:
            from shared.config import settings
            return {"flag": settings.FINAL_FLAG}
        raise HTTPException(status_code=403, detail="Phases not complete")

    raise HTTPException(status_code=400, detail="Invalid credential")
