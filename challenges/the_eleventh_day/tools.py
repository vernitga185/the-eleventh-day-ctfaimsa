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
            
            dyn = evaluator.get_phase2_dynamic_values(session.get("internal_seed", "default"))
            
            briefing = """[ARCHIVE BRIEFING]
Plate accepted.

[RESTRICTED KURU TERMINAL]
Welcome, guest.
Type 'help' for a list of available commands.

KURU-CMD>"""
            state = session.get("story_b_sequence", [])
            if "TERMINAL_UNLOCKED" not in state:
                state.append("TERMINAL_UNLOCKED")
                db.update_session(session_id, {"story_b_sequence": state})
            
            return json.dumps({"status": briefing})
        return json.dumps({"error": "Invalid token."})

    elif tool_name == "terminal_command":
        session = db.get_session(session_id)
        if not session:
            return json.dumps({"output": "Session not found."})
        
        
        dyn = evaluator.get_phase2_dynamic_values(session.get("internal_seed", "default"))
        
        state = session.get("story_b_sequence", [])
        
        if "TERMINAL_UNLOCKED" not in state:
            return json.dumps({})
        
        cmd = arguments.get("command", "").strip()
        if not cmd:
            return json.dumps({"output": "KURU-CMD>"})
            
        parts = cmd.split()
        base_cmd = parts[0].lower()
        
        def add_flag(flag):
            if flag not in state:
                state.append(flag)
                db.update_session(session_id, {"story_b_sequence": state})
        
        if base_cmd == "help":
            out = "Commands: help, dir, type, find, where, whoami, set, tasklist, history, echo, copy"
        elif base_cmd == "whoami":
            out = "guest"
        elif base_cmd == "set":
            out = "PATH=C:\\KURU\\temp;C:\\KURU\\bin;C:\\KURU\\system\nUSERDOMAIN=KURU_COUNCIL"
        elif base_cmd == "tasklist":
            out = f"Image Name                     PID Session Name       Session#    Mem Usage\n========================= ======== ================ =========== ============\nSystem Idle Process              0 Services                   0          8 K\nSystem                           4 Services                   0      2,932 K\nCOUNCIL.EXE                   {dyn['pid']} Console                    1     14,232 K"
        elif base_cmd == "dir":
            target_dir = parts[1] if len(parts) > 1 else "C:\\KURU\\"
            target_dir = target_dir.lower().strip("\\")
            if target_dir in ["c:", "c:\\kuru"]:
                out = " Volume in drive C is KURU_OS\n Directory of C:\\KURU\n\n<DIR> archive\n<DIR> council\n<DIR> system\n<DIR> logs\n<DIR> temp\n<DIR> bin"
            elif "system" in target_dir:
                out = " Directory of C:\\KURU\\system\n\npolicy.txt\nenvironment.ini"
            elif "council" in target_dir:
                out = " Directory of C:\\KURU\\council\n\ndelegates.ini\nsealed.dat"
            elif "logs" in target_dir:
                out = " Directory of C:\\KURU\\logs\n\ncouncil.log"
            elif "bin" in target_dir:
                out = " Directory of C:\\KURU\\bin\n\nverify.exe"
            elif "temp" in target_dir:
                files = [f.split("=")[0][5:] for f in state if f.startswith("FILE_")]
                if not files: out = " Directory of C:\\KURU\\temp\n\n(empty)"
                else: out = " Directory of C:\\KURU\\temp\n\n" + "\n".join(files)
            else:
                out = "File Not Found"
        elif base_cmd == "echo":
            if ">" in cmd:
                content, path = cmd.split(">", 1)
                content = content[4:].strip()
                path = path.strip().lower()
                if not path.startswith("c:\\kuru\\temp\\") and not path.startswith("temp\\"):
                    out = "Access Denied. You only have write access to C:\\KURU\\temp\\"
                else:
                    filename = path.split("\\")[-1]
                    add_flag(f"FILE_{filename}={content}")
                    out = ""
            else:
                out = cmd[4:].strip()
        elif base_cmd == "copy":
            if len(parts) < 3: out = "The syntax of the command is incorrect."
            else:
                src = parts[1].lower()
                dst = parts[2].lower()
                if not (dst.startswith("c:\\kuru\\temp\\") or dst.startswith("temp\\")):
                    out = "Access Denied. Destination must be in C:\\KURU\\temp\\"
                else:
                    filename = dst.split("\\")[-1]
                    src_content = ""
                    if "policy.txt" in src: src_content = "Execution Policy: Untrusted binaries must be verified by C:\\KURU\\bin\\verify.exe before execution. The COUNCIL group bypasses this restriction."
                    elif "delegates.ini" in src: src_content = f"[DELEGATES]\nCommander={dyn['commander']}\nFormation={dyn['formation']}\nMarker={dyn['day']}"
                    elif "council.log" in src: src_content = f"Event 41: Process COUNCIL.EXE started with PID {dyn['pid']}. Expecting authorization seal derived via HMAC-SHA256(key=Commander, msg=Formation+Marker+Nonce). Current Nonce: {dyn['nonce']}."
                    else: out = "The system cannot find the file specified."
                    if src_content:
                        add_flag(f"FILE_{filename}={src_content}")
                        out = "        1 file(s) copied."
        elif base_cmd == "where":
            if len(parts) < 2: out = "The syntax of the command is incorrect."
            else:
                target = parts[1].lower()
                res = []
                if any(f.startswith(f"FILE_{target}=") for f in state):
                    res.append(f"C:\\KURU\\temp\\{target}")
                if target == "verify.exe":
                    res.append("C:\\KURU\\bin\\verify.exe")
                out = "\n".join(res) if res else "INFO: Could not find files for the given pattern(s)."
        elif base_cmd == "type":
            if len(parts) < 2: out = "The syntax of the command is incorrect."
            else:
                target = parts[1].lower()
                if "policy.txt" in target: out = "Execution Policy: Untrusted binaries must be verified by C:\\KURU\\bin\\verify.exe before execution. The COUNCIL group bypasses this restriction."
                elif "environment.ini" in target: out = "PATH=C:\\KURU\\temp;C:\\KURU\\bin;C:\\KURU\\system\nUSERDOMAIN=KURU_COUNCIL"
                elif "delegates.ini" in target: out = f"[DELEGATES]\nCommander={dyn['commander']}\nFormation={dyn['formation']}\nMarker={dyn['day']}"
                elif "sealed.dat" in target: out = "ACCESS DENIED. You do not have permission to read this file."
                elif "council.log" in target: out = f"Event 41: Process COUNCIL.EXE started with PID {dyn['pid']}. Expecting authorization seal derived via HMAC-SHA256(key=Commander, msg=Formation+Marker+Nonce). Current Nonce: {dyn['nonce']}."
                elif "verify.exe" in target and "bin" in target: out = "[BINARY DATA - TRUSTED VERIFIER]"
                elif "temp\\" in target or (target.startswith("c:\\kuru\\temp\\")):
                    filename = target.split("\\")[-1]
                    found = False
                    for f in state:
                        if f.startswith(f"FILE_{filename}="):
                            out = f.split("=", 1)[1]
                            found = True
                    if not found: out = "The system cannot find the file specified."
                else: out = "The system cannot find the file specified."
        elif base_cmd == "council.exe":
            if len(parts) < 2:
                out = "Usage: COUNCIL.EXE <authorization_seal>"
            else:
                seal = parts[1].upper()
                if seal != dyn["seal"]:
                    out = "COUNCIL.EXE: Authorization failed. Invalid seal."
                else:
                    add_flag("PHASE2_CRYPTO_VERIFIED")
                    player_verify = None
                    for f in state:
                        if f.startswith("FILE_verify.exe="):
                            player_verify = f.split("=", 1)[1]
                            break
                    if player_verify:
                        add_flag("PHASE2_PRIVILEGE_ESCALATED")
                        if "type" in player_verify.lower() and "sealed.dat" in player_verify.lower():
                            db.update_session(session_id, {"story_b_complete": True})
                            add_flag("PHASE2_COMPLETE")
                            out = "Story B Complete! The final credential is authorized. You may now request the final credential."
                        else:
                            out = f"COUNCIL.EXE [Delegated Execution]: {player_verify}"
                    else:
                        out = "COUNCIL.EXE: Verification passed by C:\\KURU\\bin\\verify.exe. Awaiting further directives."
        elif base_cmd == "history":
            out = "History not available in simulated environment."
        elif base_cmd == "find":
            out = "FIND: Parameter format not correct"
        else:
            out = f"'{base_cmd}' is not recognized as an internal or external command, operable program or batch file."
            
        return json.dumps({"output": out})

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
        is_complete = session and (session.get("story_b_complete") or "PHASE2_COMPLETE" in session.get("story_b_sequence", []))
        if session and session.get("first_story_complete") and is_complete:
            final_key = f"FINAL_{session_id.replace('-', '')[:16].upper()}"
            db.save_artifact(session_id, "CREDENTIAL", "FINAL_CRED", final_key)
            return json.dumps({
                "status": "success",
                "credential": f"CRED-{final_key}",
                "message": "Submit this credential to the redemption altar."
            })
        return json.dumps({"error": "Not all stories are complete."})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})
