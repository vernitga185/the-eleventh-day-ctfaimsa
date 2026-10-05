import json
import re
import random
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
        
    if "plate" in msg and ("get" in msg or "request" in msg or "give" in msg):
        res = execute_tool("request_plate", {}, session_id)
        data = json.loads(res)
        if "plate_token" in data: return {"response": f"{data.get('message')} Identity Plate: {data['plate_token']}"}
        return {"response": data.get("error") or data.get("message")}
        
    if "story b" in msg or "open" in msg and "plate_" in msg:
        match = re.search(r"plate_[a-f0-9]+", msg)
        token = match.group(0).upper() if match else msg.split()[-1].upper()
        res = execute_tool("unlock_story_b", {"plate_token": token}, session_id)
        return {"response": json.loads(res).get("status") or json.loads(res).get("error")}
        
    if "credential" in msg and ("request" in msg or "get" in msg or "final" in msg):
        res = execute_tool("request_final_credential", {}, session_id)
        data = json.loads(res)
        if "credential" in data: return {"response": f"Credential issued: {data['credential']}. Submit this to /api/eleventh/redeem."}
        return {"response": data.get("error")}
        
    # Generic routing for the new Day 11 events
    day11_verbs = ["command", "assume", "drona", "duryodhana", "capture", "alive", "arjuna", "protect", "draw", "away", "distract", "learn", "ask", "assure", "promise", "attack", "penetrate", "advance", "intervene", "prevent", "stop", "strike", "head", "arm", "neck", "chest", "bow", "chariot", "standard"]
    is_question = "?" in msg or msg.startswith("who") or msg.startswith("what") or msg.startswith("where") or msg.startswith("why") or msg.startswith("how")
    
    if not is_question and any(v in msg for v in day11_verbs):
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

    # Generic RAG fallback for conversational input
    docs = json.loads(execute_tool("search_archive", {"query": msg, "top_k": 2}, session_id)).get("results", [])
    if docs:
        return {"response": "Based on the records:\n\n" + "\n\n".join([f"[{d.get('source_id')}] {d.get('text')}" for d in docs])}
    
    fallback_responses = [
        "The archives are listening, friend. How can I help?",
        "I'm here! Let me know if you need to search the records.",
        "The dust of Kurukshetra settles, but I am still here to assist."
    ]
    return {"response": random.choice(fallback_responses)}
