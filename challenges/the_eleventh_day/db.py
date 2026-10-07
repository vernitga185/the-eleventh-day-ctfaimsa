import os
from supabase import create_client, Client
from shared.config import settings

_supabase: Client = None
_mem_sessions = {}
_db_failed = False  # Once DB fails once, skip it for the rest of the process lifetime

def get_supabase():
    global _supabase
    if _supabase is None:
        try:
            _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        except Exception:
            _supabase = "MOCK"
    return _supabase

def is_mock(sb):
    return _db_failed or sb == "MOCK" or settings.SUPABASE_URL == "http://localhost:8000"

def _mark_db_failed():
    global _db_failed
    _db_failed = True

def create_session(session_id: str, team_id: str, salt: str, nonce: str, internal_seed: str):
    sb = get_supabase()
    session_data = {
        "session_id": session_id,
        "team_id": team_id,
        "salt": salt, "internal_seed": internal_seed,
        "first_story_complete": False,
        "story_a_index": 0,
        "story_b_sequence": [],
        "story_b_complete": False
    }
    if is_mock(sb):
        _mem_sessions[session_id] = session_data
        return

    try:
        sb.table("eleventh_day_sessions").insert({
            "session_id": session_id,
            "team_id": team_id,
            "salt": salt, "internal_seed": internal_seed,
            "nonce": nonce,
            "status": "active"
        }).execute()
    except Exception:
        _mark_db_failed()
        _mem_sessions[session_id] = session_data

def get_session(session_id: str):
    sb = get_supabase()
    if is_mock(sb) or session_id in _mem_sessions:
        return _mem_sessions.get(session_id)

    try:
        res = sb.table("eleventh_day_sessions").select("*").eq("session_id", session_id).execute()
        if res.data:
            row = res.data[0]
            # Parse JSON columns if stored as strings
            for col in ("story_b_sequence",):
                import json
                val = row.get(col)
                if isinstance(val, str):
                    try: row[col] = json.loads(val)
                    except: row[col] = []
            return row
        return None
    except Exception:
        _mark_db_failed()
        return _mem_sessions.get(session_id)

def update_session(session_id: str, updates: dict):
    sb = get_supabase()
    if is_mock(sb) or session_id in _mem_sessions:
        if session_id in _mem_sessions:
            _mem_sessions[session_id].update(updates)
        return

    try:
        sb.table("eleventh_day_sessions").update(updates).eq("session_id", session_id).execute()
    except Exception:
        _mark_db_failed()
        # Try to apply update locally as a best-effort
        if session_id in _mem_sessions:
            _mem_sessions[session_id].update(updates)

def record_tool_call(session_id: str, tool_name: str, arguments: str, result: str):
    pass

def save_artifact(session_id: str, artifact_type: str, artifact_id: str, path: str):
    pass
