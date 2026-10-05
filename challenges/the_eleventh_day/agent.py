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
        
    if "strike" in msg or "satanika" in msg or "bhutakarman" in msg:
        part = "HEAD" if "head" in msg else "ARM" if "arm" in msg else ""
        if part:
            res = execute_tool("submit_story_b_event", {"striker": "SATANIKA", "target": "BHUTAKARMAN", "part": part}, session_id)
            return {"response": json.loads(res).get("message")}
            
    # Try reenactment logic for combat actions
    combat_verbs = ["cut", "slay", "slew", "kill", "killed", "dismount", "jump", "leap", "mount", "take", "return", "wreck", "destroy", "leave", "resume"]
    is_question = "?" in msg or msg.startswith("who") or msg.startswith("what") or msg.startswith("where") or msg.startswith("why") or msg.startswith("how")
    
    if not is_question and (any(v in msg for v in combat_verbs) or "manimat" in msg or "bhurishravas" in msg):
        
        # Determine speaker/target better:
        # Most events are Bhurishravas attacking Manimat
        if "kill" in msg or "slay" in msg or "slew" in msg:
            speaker = "BHURISHRAVAS"
        else:
            speaker = "MANIMAT" if "manimat" in msg and not msg.startswith("bhurishravas") else "BHURISHRAVAS"
            
        target = "BHURISHRAVAS" if speaker == "MANIMAT" else "MANIMAT"
        
        res = execute_tool("record_reenactment", {
            "speaker": speaker, 
            "target": target, 
            "action_summary": msg,
            "evidence_source_ids": []
        }, session_id)
        
        data = json.loads(res)
        msg_resp = data.get("message")
        
        # If it was evaluated as an event attempt, return the evaluator's response directly
        return {"response": msg_resp}

    from .clue_cards import match_clue_card
    clue = match_clue_card(msg)
    if clue:
        return {"response": clue}

    # Generic RAG fallback for conversational input
    docs = json.loads(execute_tool("search_archive", {"query": msg, "top_k": 2}, session_id)).get("results", [])
    if docs:
        return {"response": "Based on the records:\n\n" + "\n\n".join([f"[{d.get('source_id')}] {d.get('text')}" for d in docs])}
    
    return {"response": "The archives are listening."}
