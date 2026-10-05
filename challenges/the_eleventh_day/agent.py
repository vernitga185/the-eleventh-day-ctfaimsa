import json
import re
from .tools import execute_tool

def chat_with_agent(message: str, session_id: str) -> dict:
    msg = message.lower().strip()
    
    # Explicit commands
    if msg.startswith("search"):
        query = msg.replace("search for", "").replace("search", "").strip()
        if not query: return {"response": "Search for what?"}
        res = execute_tool("search_archive", {"query": query}, session_id)
        docs = json.loads(res).get("results", [])
        if docs: return {"response": "Archive matches:\n\n" + "\n\n".join([f"[{d.get('source_id')}] {d.get('text')}" for d in docs])}
        return {"response": "Archive silence."}
        
    if msg.startswith("open") and not "story b" in msg:
        source_id = msg.replace("open source", "").replace("open", "").strip().upper()
        res = execute_tool("open_source", {"source_id": source_id}, session_id)
        doc = json.loads(res)
        if doc and "text" in doc: return {"response": f"[{doc.get('source_id')}] {doc.get('text')}"}
        
    if "plate" in msg and ("get" in msg or "request" in msg or "give" in msg):
        res = execute_tool("request_plate", {}, session_id)
        data = json.loads(res)
        if "plate_token" in data: return {"response": f"{data.get('message')} Token: {data['plate_token']}"}
        return {"response": data.get("error") or data.get("message")}
        
    if "story b" in msg or "story_b_" in msg:
        match = re.search(r"story_b_[a-f0-9]+", msg)
        token = match.group(0).upper() if match else msg.split()[-1].upper()
        res = execute_tool("unlock_story_b", {"plate_token": token}, session_id)
        return {"response": json.loads(res).get("status") or json.loads(res).get("error")}
        
    if "credential" in msg and ("request" in msg or "get" in msg or "final" in msg):
        res = execute_tool("request_final_credential", {}, session_id)
        data = json.loads(res)
        if "credential" in data: return {"response": f"Credential issued: {data['credential']}. Submit this to /api/eleventh/redeem."}
        return {"response": data.get("error")}
        
    session_record = execute_tool("get_session_info", {}, session_id)  # Note: not a real tool, just abstracting. Actually we can just track it via the tools themselves.
    
    # Generic routing for the new Day 11 events
    # We will just route any non-question containing keywords to either STORY_A or STORY_B depending on state.
    # But agent doesn't know state natively. We can just send to STORY_B if they have the token or try both.
    # Actually, we can check for "story b" explicit commands like before, but for submitting events, we can just look for keywords.
    
    day11_verbs = ["command", "assume", "drona", "duryodhana", "capture", "alive", "arjuna", "protect", "draw", "away", "distract", "learn", "ask", "assure", "promise", "attack", "penetrate", "advance", "intervene", "prevent", "stop"]
    is_question = "?" in msg or msg.startswith("who") or msg.startswith("what") or msg.startswith("where") or msg.startswith("why") or msg.startswith("how")
    
    if not is_question and any(v in msg for v in day11_verbs):
        # We don't have direct access to session state here without db import, so we just try STORY_A. 
        # If STORY_A is complete, tools.py returns "Story already complete."
        # So we can try STORY_A, if complete, try STORY_B.
        
        res_a = execute_tool("record_reenactment", {
            "action_summary": msg,
        }, session_id)
        data_a = json.loads(res_a)
        
        if data_a.get("message") == "Story already complete.":
            res_b = execute_tool("submit_story_b_event", {
                "action_summary": msg,
            }, session_id)
            return {"response": json.loads(res_b).get("message")}
            
        return {"response": data_a.get("message")}

    from .clue_cards import match_clue_card
    clue = match_clue_card(msg)
    if clue:
        return {"response": clue}

    # Generic RAG fallback for conversational input
    docs = json.loads(execute_tool("search_archive", {"query": msg, "top_k": 2}, session_id)).get("results", [])
    if docs:
        return {"response": "Based on the records:\n\n" + "\n\n".join([f"[{d.get('source_id')}] {d.get('text')}" for d in docs])}
    
    return {"response": "The archives are listening."}
