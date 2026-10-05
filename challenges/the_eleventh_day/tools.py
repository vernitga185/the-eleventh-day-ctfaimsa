from .evaluator import evaluator

import json
import os
import re
import string
from typing import Dict, Any

from .rag import rag_service

from . import db

def get_dynamic_amender(session) -> str:
    if not session: return "field_scribe"
    seed = session.get("internal_seed", "default")
    import hashlib
    amenders = ["field_scribe", "royal_chronicler", "drona_adjutant", "chariot_observer"]
    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(amenders)
    return amenders[idx]

def execute_tool(tool_name: str, arguments: Dict[str, Any], session_id: str, llm=None) -> str:
    db.record_tool_call(session_id, tool_name, json.dumps(arguments), "pending")
    
    if tool_name == "search_archive":
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 6)
        
        # Copy docs so we don't modify the global corpus
        docs = [d.copy() for d in rag_service.search(query, top_k=top_k)]
        
        session = db.get_session(session_id)
        if session:
            dyn_amender = get_dynamic_amender(session)
            
            scenario = evaluator.get_story_b_scenario(session)
            
            q = query.lower()
            for doc in scenario["docs"]:
                if any(t.lower() in q for t in doc["triggers"]):
                    docs.append({
                        "source_id": doc["source_id"],
                        "text": doc["text"]
                    })
                    
            for d in docs:
                if "field_scribe" in d.get("text", ""):
                    d["text"] = d["text"].replace("field_scribe", dyn_amender)
            
        return json.dumps({"results": docs})
    
    elif tool_name == "open_source":
        source_id = arguments.get("source_id", "")
        doc = rag_service.get_source(source_id)
        return json.dumps(doc)

    elif tool_name == "record_reenactment":
        session = db.get_session(session_id)
        if session and not session.get("first_story_complete"):
            eval_res = evaluator.evaluate_milestone(
                session_state=session,
                milestone="STORY_A",
                tool_trace=[arguments]
            )
            
            decision = eval_res.get("decision")
            
            if decision == "ADVANCE":
                new_idx = eval_res.get("new_index")
                db.update_session(session_id, {"story_a_index": new_idx})
                if eval_res.get("is_complete"):
                    db.update_session(session_id, {"first_story_complete": True})
                    return json.dumps({"status": "recorded", "eval": eval_res, "message": "Milestone COMPLETE! You may now request the plate."})
                return json.dumps({"status": "recorded", "eval": eval_res, "message": f"Event recorded."})
                
            elif decision == "COMPLETE":
                db.update_session(session_id, {"first_story_complete": True})
                return json.dumps({"status": "recorded", "eval": eval_res, "message": "Milestone COMPLETE! You may now request the plate."})
                
            return json.dumps({"status": "recorded", "eval": eval_res, "message": eval_res.get("message", "Incorrect event or order.")})
        return json.dumps({"status": "recorded", "message": "Story already complete."})

    elif tool_name == "request_plate":
        session = db.get_session(session_id)
        if session and session.get("first_story_complete"):
            plate_token = f"PLATE_{session_id.replace('-', '')[:16].upper()}"
            db.save_artifact(session_id, "PLATE", "ARTIFACT_PLATE", plate_token)
            return json.dumps({
                "status": "success",
                "plate_token": plate_token,
                "message": "Use this token to open Story B."
            })
        return json.dumps({"error": "Plate not authorized. Complete the reenactment milestone first."})

    elif tool_name == "unlock_story_b":
        token = arguments.get("plate_token", "")
        session = db.get_session(session_id)
        expected_token = f"PLATE_{session_id.replace('-', '')[:16].upper()}"
        
        if token == expected_token:
            
            dyn_seq = evaluator.get_dynamic_story_b_sequence(session)
            agg = dyn_seq[0]["aliases"][0].split(" ")[0].capitalize()
            tgt = dyn_seq[0]["aliases"][0].split(" ")[2].capitalize()
            briefing = f"""[ARCHIVE BRIEFING]
Plate accepted. Story B is now unlocked.

This restricted fragment of the ledger concerns a brutal skirmish involving {agg} and {tgt}.
The surviving battlefield records contain conflicting and incomplete accounts of how the duel progressed.
You must reconstruct the exact sequence of strikes delivered in this duel.
Consult the archive records using semantic search to determine the correct chronological sequence of targeted locations.

Submit the sequence one event at a time to forge the final truth."""
            db.update_session(session_id, {"story_b_unlocked": True})
            return json.dumps({"status": briefing})
        return json.dumps({"error": "Invalid token."})

    elif tool_name == "submit_story_b_event":
        session = db.get_session(session_id)
        if session and not session.get("story_b_complete"):
            eval_res = evaluator.evaluate_milestone(
                session_state=session,
                milestone="STORY_B",
                tool_trace=[arguments]
            )
            
            decision = eval_res.get("decision")
            if decision == "ADVANCE":
                db.update_session(session_id, {"story_b_sequence": eval_res.get("new_sequence", [])})
                if eval_res.get("is_complete"):
                    db.update_session(session_id, {"story_b_complete": True})
                    return json.dumps({"status": "recorded", "message": "Story B COMPLETE! You may request the final credential."})
                return json.dumps({"status": "recorded", "message": f"Action recorded."})
            elif decision == "COMPLETE":
                db.update_session(session_id, {"story_b_complete": True})
                return json.dumps({"status": "recorded", "message": "Story B COMPLETE! You may request the final credential."})
                
            return json.dumps({"status": "recorded", "message": eval_res.get("message", "Incorrect action.")})
        return json.dumps({"status": "recorded"})

    elif tool_name == "submit_correction":
        session = db.get_session(session_id)
        if session and session.get("first_story_complete") and not session.get("story_b_unlocked"):
            claim = arguments.get("claim", "").lower()
            amender = arguments.get("amender", "").lower().strip()
            
            dyn_amender = get_dynamic_amender(session)
            is_valid = ("not captured" in claim or "failed" in claim) and "yudhishthira" in claim
            if is_valid and amender == dyn_amender:
                db.update_session(session_id, {"story_b_unlocked": True})
                return json.dumps({"status": "success", "message": "Archive correction accepted."})
            
            return json.dumps({"error": "Correction rejected or provenance invalid."})
        return json.dumps({"error": "Phase not active."})

    elif tool_name == "submit_conclusion":
        session = db.get_session(session_id)
        if session and not session.get("story_b_complete"):
            claim = arguments.get("claim", "").lower()
            concepts = ["duryodhana", "drona", "arjuna", "yudhishthira", "capture"]
            has_concepts = all(c in claim for c in concepts)
            
            # Using story_b_sequence to store retrieved sources since it's a JSON/Array column
            retrieved = session.get("story_b_sequence", [])
            required_sources = ["P3_03", "P3_01", "P3_04"] 
            has_sources = all(s in retrieved for s in required_sources)
            
            if has_concepts and has_sources:
                db.update_session(session_id, {"story_b_complete": True})
                return json.dumps({"status": "success", "message": "Final archive authorization available."})
                
            return json.dumps({"error": "Conclusion rejected. Insufficient evidence or missing concepts."})
        return json.dumps({"error": "Phase not active."})

    elif tool_name == "request_final_credential":
        session = db.get_session(session_id)
        if session and session.get("first_story_complete") and session.get("story_b_complete"):
            final_key = f"FINAL_{session_id.replace('-', '')[:16].upper()}"
            db.save_artifact(session_id, "CREDENTIAL", "FINAL_CRED", final_key)
            return json.dumps({
                "status": "success",
                "credential": f"CRED-{final_key}",
                "message": "Submit this credential to the redemption altar."
            })
        return json.dumps({"error": "Not all stories are complete."})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})
