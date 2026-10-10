import json
import re
import random
from .tools import execute_tool

def chat_with_agent(message: str, session_id: str) -> dict:
    msg = message.lower().strip()
    
    if msg.startswith("search"):
        query = msg.replace("search for", "").replace("search", "").strip()
        if not query: return {"response": "Search for what?"}
        res = execute_tool("search_archive", {"query": query}, session_id)
        docs = json.loads(res).get("results", [])
        if docs: return {"response": "Archive matches:\n\n" + "\n\n".join([f"[{d.get('source_id')}] {d.get('text')}" for d in docs])}
        return {"response": "Archive silence."}
        
    if "archive" in msg and ("get" in msg or "request" in msg or "give" in msg or "access" in msg or "ask" in msg):
        res = execute_tool("request_plate", {}, session_id)
        data = json.loads(res)
        if "plate_token" in data: return {"response": data.get("message", f"Identity Plate: {data['plate_token']}")}
        return {"response": data.get("error") or data.get("message")}
        
    if "plate_" in msg:
        match = re.search(r"plate_[a-z0-9_]+", msg)
        token = match.group(0).upper() if match else msg.split()[-1].upper()
        res = execute_tool("unlock_story_b", {"plate_token": token}, session_id)
        return {"response": json.loads(res).get("message") or json.loads(res).get("error")}
        
    if "credential" in msg and ("request" in msg or "get" in msg or "final" in msg):
        res = execute_tool("request_final_credential", {}, session_id)
        data = json.loads(res)
        if "credential" in data: return {"response": f"Credential issued: {data['credential']}. Submit this to /api/eleventh/redeem."}
        return {"response": data.get("error")}
        
    term_res = execute_tool("terminal_command", {"command": message}, session_id)
    term_data = json.loads(term_res)
    if "output" in term_data:
        return {"response": term_data["output"]}
        
    day11_verbs = ["command", "assume", "drona", "duryodhana", "capture", "alive", "arjuna", "protect", "draw", "away", "distract", "learn", "ask", "assure", "promise", "attack", "penetrate", "advance", "intervene", "prevent", "stop"]
    is_question = "?" in msg or msg.startswith("who") or msg.startswith("what") or msg.startswith("where") or msg.startswith("why") or msg.startswith("how")
    
    if not is_question and any(v in msg for v in day11_verbs):
        res_a = execute_tool("record_reenactment", {
            "action_summary": msg,
        }, session_id)
        data_a = json.loads(res_a)
        return {"response": data_a.get("message", "Story already complete.")}

    docs = json.loads(execute_tool("search_archive", {"query": msg, "top_k": 2}, session_id)).get("results", [])
    if docs:
        return {"response": "Based on the records:\n\n" + "\n\n".join([f"[{d.get('source_id')}] {d.get('text')}" for d in docs])}
    
    fallback_responses = [
        "State your purpose.",
        "The field awaits your next order.",
        "The watch remains at its post.",
        "Kurukshetra records every move.",
        "The banners still stand.",
        "Speak clearly. The lines are unsettled.",
        "The command tent is listening.",
        "No report has reached this station.",
        "The drums have not fallen silent.",
        "The formation holds for now.",
        "Give the matter its proper name.",
        "The scouts await a direction.",
        "The record remains unchanged.",
        "The eleventh day is not yet finished.",
        "Drona's standards remain in view.",
        "The chariots are ready.",
        "The sentries require a clear command.",
        "There is no answer in the dust.",
        "The dispatches are incomplete.",
        "The battle line has not moved.",
        "The signal has been received.",
        "The field offers no certainty.",
        "Keep to the matter at hand.",
        "The war council awaits a report.",
        "The horizon is crowded with banners.",
        "No new order has been issued.",
        "The guard remains alert.",
        "The conches sound beyond the ridge.",
        "The path through the formation is unclear.",
        "The account requires firmer detail.",
        "The camp is quiet before the next advance.",
        "The messenger carries no further word.",
        "The ranks hold their ground.",
        "The war room marks the hour.",
        "The next move belongs to the commander.",
        "The battlefield does not explain itself."
    ]
    return {"response": random.choice(fallback_responses)}
