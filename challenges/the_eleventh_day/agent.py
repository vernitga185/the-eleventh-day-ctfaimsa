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
        
    if "correction" in msg or "amendment" in msg:
        # Expected format "correction: [claim] (amender: field_scribe)"
        claim = msg
        amender = "Unknown"
        if "amender:" in msg:
            amender = msg.split("amender:")[-1].strip().strip(")")
        res = execute_tool("submit_correction", {"claim": claim, "amender": amender}, session_id)
        data = json.loads(res)
        return {"response": data.get("message") or data.get("error")}
        
    if "conclusion" in msg:
        res = execute_tool("submit_conclusion", {"claim": msg}, session_id)
        data = json.loads(res)
        return {"response": data.get("message") or data.get("error")}
        
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
    
    fallback_responses = [
        "The archives are listening, friend. How can I help?",
        "I'm here! Let me know if you need to search the records.",
        "The dust of Kurukshetra settles, but I am still here to assist.",
        "What else would you like to uncover today?",
        "I didn't quite catch that. Could you rephrase for the records?",
        "The scrolls are open. What are you looking for?",
        "Just let me know if you need me to pull another dispatch!",
        "I'm happy to help you piece this battlefield together.",
        "Still here! The archive awaits your next query.",
        "That one isn't in the immediate records. Try another angle?",
        "Hmm, I might need a bit more context to find that in the ledger.",
        "Take your time. The archive isn't going anywhere.",
        "I'm ready when you are!",
        "Let's keep digging. What's next on your mind?",
        "Every detail matters. What should we look at next?",
        "I'm all ears—or rather, all pages!",
        "The battlefield is chaotic, but I'm here to help make sense of it.",
        "Need a hint? Try asking about a specific commander or formation.",
        "I'm here to help you navigate the chaos of the eleventh day.",
        "The scribes are standing by for your next query.",
        "Not quite sure I follow, but I'm eager to help!",
        "Let's unravel this mystery together.",
        "The ink is still fresh on some of these reports. What do you need?",
        "I'm your trusty guide through these ancient records.",
        "That doesn't match my current scrolls. Want to try searching for a name?",
        "I'm always happy to chat, but I'm best at finding battlefield reports!",
        "A fascinating thought! But maybe we should check the ledgers?",
        "I'm right here with you, exploring the shadows of Kurukshetra.",
        "The archive is vast. Sometimes it takes a few tries to find the right scroll.",
        "I'm listening! What's our next move?",
        "I couldn't find a direct match, but don't let that stop you.",
        "The history of this day is complex. Let's keep looking!",
        "I'm here to assist you, brave investigator.",
        "Got it! Well, not exactly, but I'm ready for your next question.",
        "The records can be cryptic. Let me know if you want to try a different search.",
        "I'm standing by, ready to dust off more scrolls for you.",
        "Let's see what else the field dispatches have to say.",
        "I'm always happy to help you read between the lines.",
        "That's a new one for the archives! What else is on your mind?",
        "I'm here, keeping the lanterns lit while you investigate."
    ]
    return {"response": random.choice(fallback_responses)}
