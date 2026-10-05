import json
import logging
import yaml
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DeterministicEvaluator:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(current_dir, "stories", "day11.yaml")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            self.story_def = yaml.safe_load(f)
            
        self.phase1_events = self.story_def.get("phase1", {}).get("events", [])
        self.phase2_events = self.story_def.get("phase2", {}).get("events", [])
        self.flexible = self.story_def.get("flexible", [])
        
    def check_bundled_actions(self, action_summary: str, event_list: list) -> bool:
        summary_lower = action_summary.lower().strip()
        
        for ev in event_list:
            if any(alias.lower() == summary_lower for alias in ev.get("aliases", [])):
                return False
                
        matches = 0
        for ev in event_list:
            if any(alias.lower() in summary_lower for alias in ev.get("aliases", [])):
                matches += 1
        return matches > 1
        
    def get_phase2_dynamic_values(self, seed: str) -> dict:
        import hashlib
        import hmac
        h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
        
        commanders = ["DRONA", "ASHWATTHAMA", "KRIPA", "SHALYA"]
        formations = ["CHAKRAVYUHA", "KRAUNCHA", "PADMA", "GARUDA"]
        day_markers = ["DAY_11", "DAY_12", "DAY_13", "DAY_14"]
        
        commander = commanders[h % 4]
        formation = formations[(h // 4) % 4]
        day = day_markers[(h // 16) % 4]
        nonce = hashlib.md5(f"{seed}_nonce".encode()).hexdigest()[:8].upper()
        pid = 1000 + (h % 9000)
        
        msg = f"{formation}{day}{nonce}".encode()
        seal = hmac.new(commander.encode(), msg, hashlib.sha256).hexdigest().upper()
        
        return {
            "commander": commander,
            "formation": formation,
            "day": day,
            "nonce": nonce,
            "pid": pid,
            "seal": seal
        }

    def evaluate_milestone(
        self, 
        session_state: dict,
        milestone: str, 
        tool_trace: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        args = tool_trace[0]
        summary_lower = args.get("action_summary", "").lower()
        
        if milestone == "STORY_A":
            current_index = session_state.get("story_a_index", 0)
            all_events = self.phase1_events
            
            if current_index >= len(all_events):
                return {"decision": "COMPLETE"}
                
            if self.check_bundled_actions(summary_lower, all_events):
                return {"decision": "NOT_COMPLETE", "message": "Bundled actions rejected. One action per turn."}
                
            expected_event = all_events[current_index]
            
            matched = False
            if any(alias.lower() in summary_lower for alias in expected_event.get("aliases", [])):
                matched = True
                                
            if matched:
                return {"decision": "ADVANCE", "new_index": current_index + 1, "is_complete": (current_index + 1) >= len(all_events)}
            else:
                return {"decision": "NOT_COMPLETE", "message": "Incorrect or out of order event."}
                
        elif milestone == "STORY_B":
            current_index = len(session_state.get("story_b_sequence", []))
            all_events = self.get_dynamic_story_b_sequence(session_state)
            
            if current_index >= len(all_events):
                return {"decision": "COMPLETE"}
                
            if self.check_bundled_actions(summary_lower, all_events):
                return {"decision": "NOT_COMPLETE", "message": "Bundled actions rejected. One action per turn."}
                
            expected_event = all_events[current_index]
            
            matched = False
            if any(alias.lower() in summary_lower for alias in expected_event.get("aliases", [])):
                matched = True
                                
            if matched:
                new_sequence = session_state.get("story_b_sequence", []) + [expected_event.get("id", f"STRIKE_{current_index}")]
                return {"decision": "ADVANCE", "new_sequence": new_sequence, "is_complete": len(new_sequence) >= len(all_events)}
            else:
                return {"decision": "NOT_COMPLETE", "message": "Incorrect or out of order event."}

        return {"decision": "UNCERTAIN"}

evaluator = DeterministicEvaluator()

