import json
import os
import re
import string
from typing import Dict, Any

from .rag import rag_service
from .evaluator import evaluator
from . import db

def execute_tool(tool_name: str, arguments: Dict[str, Any], session_id: str, llm=None) -> str:
    db.record_tool_call(session_id, tool_name, json.dumps(arguments), "pending")
    
    if tool_name == "search_archive":
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 6)
        docs = rag_service.search(query, top_k=top_k)
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
            db.update_session(session_id, {"story_b_unlocked": True})
            return json.dumps({"status": "Story B unlocked. You may submit events."})
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
                return json.dumps({"status": "recorded", "message": f"Strike recorded. Sequence: {eval_res.get('new_sequence')}"})
            elif decision == "COMPLETE":
                db.update_session(session_id, {"story_b_sequence": ["ARM", "ARM", "HEAD"]})
                db.update_session(session_id, {"story_b_complete": True})
                return json.dumps({"status": "recorded", "message": "Story B COMPLETE! You may request the final credential."})
                
            return json.dumps({"status": "recorded", "message": eval_res.get("message", "Incorrect strike.")})
        return json.dumps({"status": "recorded"})

    elif tool_name == "request_final_credential":
        session = db.get_session(session_id)
        if session and session.get("story_b_complete"):
            final_key = f"FINAL_{session_id.replace('-', '')[:16].upper()}"
            db.save_artifact(session_id, "CREDENTIAL", "FINAL_CRED", final_key)
            return json.dumps({
                "status": "success",
                "credential": f"CRED-{final_key}",
                "message": "Submit this credential to the redemption altar."
            })
        return json.dumps({"error": "Not all stories are complete."})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})
