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
        
    def get_story_b_scenario(self, session_state: dict) -> dict:
        import hashlib
        seed = session_state.get("internal_seed", "default_seed")
        hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)
        
        scenarios = [
            {
                "aggressor": "Satanika",
                "target": "Ashwatthama",
                "sequence": [
                    {"aliases": ["satanika cut the standard", "cut the standard", "strike standard", "satanika strike ashwatthama standard"]},
                    {"aliases": ["satanika strike the chariot", "strike chariot", "strike the chariot", "satanika strike ashwatthama chariot"]},
                    {"aliases": ["satanika strike the neck", "strike neck", "strike the neck", "satanika strike ashwatthama neck"]}
                ],
                "docs": [
                    {"source_id": "DYN_REPORT_A1", "triggers": ["satanika", "ashwatthama", "skirmish"], "text": "[DISPATCH] A brutal skirmish broke out on the southern flank between Satanika and Ashwatthama."},
                    {"source_id": "DYN_OBS_A2", "triggers": ["ashwatthama", "standard", "chariot", "strike"], "text": "[WITNESS_ACCOUNT] I saw Satanika's first strike shatter the standard. Shortly after, the chariot itself took a heavy blow."},
                    {"source_id": "DYN_MED_A3", "triggers": ["satanika", "neck", "strike", "final"], "text": "[MEDIC_REPORT] The final decisive blow landed squarely on the neck."},
                    {"source_id": "DYN_DEC_A4", "triggers": ["chariot", "standard", "first"], "text": "[RUMOR] Some say the chariot was struck first, but they were not at the front lines."}
                ]
            },
            {
                "aggressor": "Shikhandi",
                "target": "Bhutakarman",
                "sequence": [
                    {"aliases": ["shikhandi cut the bow", "cut the bow", "strike bow", "shikhandi strike bhutakarman bow"]},
                    {"aliases": ["shikhandi strike the arm", "strike arm", "strike the arm", "shikhandi strike bhutakarman arm"]},
                    {"aliases": ["shikhandi strike the head", "strike head", "strike the head", "shikhandi strike bhutakarman head"]}
                ],
                "docs": [
                    {"source_id": "DYN_REPORT_B1", "triggers": ["shikhandi", "bhutakarman", "skirmish"], "text": "[FIELD_REPORT] Shikhandi engaged Bhutakarman in a fierce duel near the center formation."},
                    {"source_id": "DYN_OBS_B2", "triggers": ["bhutakarman", "bow", "arm", "strike"], "text": "[OBSERVATION] Bhutakarman's bow was the first to fall, snapped in half. Then a vicious strike caught his arm."},
                    {"source_id": "DYN_MED_B3", "triggers": ["shikhandi", "head", "strike", "fatal"], "text": "[CORPSE_EXAMINATION] The fatal injury was a severe trauma to the head, delivered as the final strike."},
                    {"source_id": "DYN_DEC_B4", "triggers": ["head", "bow", "first"], "text": "[CONFLICTING_ACCOUNT] A scribe noted the head was struck before the bow broke, but the timestamps are contested."}
                ]
            },
            {
                "aggressor": "Dhrishtadyumna",
                "target": "Kritavarma",
                "sequence": [
                    {"aliases": ["dhrishtadyumna strike the chest", "strike chest", "strike the chest", "dhrishtadyumna strike kritavarma chest"]},
                    {"aliases": ["dhrishtadyumna dismount", "dismount", "forced to dismount", "dhrishtadyumna force kritavarma dismount"]},
                    {"aliases": ["dhrishtadyumna strike the neck", "strike neck", "strike the neck", "dhrishtadyumna strike kritavarma neck"]}
                ],
                "docs": [
                    {"source_id": "DYN_REPORT_C1", "triggers": ["dhrishtadyumna", "kritavarma", "skirmish"], "text": "[TACTICAL_SUMMARY] Dhrishtadyumna clashed violently with Kritavarma."},
                    {"source_id": "DYN_OBS_C2", "triggers": ["kritavarma", "chest", "dismount", "clash"], "text": "[EYEWITNESS] The initial clash resulted in a heavy strike to the chest. Following this, one of the warriors was forced to dismount."},
                    {"source_id": "DYN_MED_C3", "triggers": ["dhrishtadyumna", "neck", "strike", "final"], "text": "[FINAL_MOMENTS] The skirmish ended with a swift strike to the neck after the dismount."},
                    {"source_id": "DYN_DEC_C4", "triggers": ["dismount", "chest", "foot"], "text": "[RUMOR] I heard Kritavarma was never on foot during the engagement."}
                ]
            },
            {
                "aggressor": "Yudhamanyu",
                "target": "Kripacharya",
                "sequence": [
                    {"aliases": ["yudhamanyu kill the charioteer", "kill charioteer", "kill the charioteer", "yudhamanyu kill kripacharya charioteer"]},
                    {"aliases": ["yudhamanyu cut the bow", "cut bow", "cut the bow", "yudhamanyu cut kripacharya bow"]},
                    {"aliases": ["yudhamanyu strike the chest", "strike chest", "strike the chest", "yudhamanyu strike kripacharya chest"]}
                ],
                "docs": [
                    {"source_id": "DYN_REPORT_D1", "triggers": ["yudhamanyu", "kripacharya", "skirmish"], "text": "[FRONT_LINE_LOG] Yudhamanyu intercepted Kripacharya's advance."},
                    {"source_id": "DYN_OBS_D2", "triggers": ["kripacharya", "charioteer", "bow", "move"], "text": "[CHARIOT_REPORT] The opening move was ruthless; the charioteer was killed instantly, followed by the severing of the bow."},
                    {"source_id": "DYN_MED_D3", "triggers": ["yudhamanyu", "chest", "strike", "conclude"], "text": "[MEDICAL_TENT] Kripacharya suffered a massive impact to the chest to conclude the duel."},
                    {"source_id": "DYN_DEC_D4", "triggers": ["bow", "charioteer", "first"], "text": "[DECOY] Some claim the bow was severed before the charioteer fell, but the dust obscured the view."}
                ]
            }
        ]
        
        return scenarios[hash_val % len(scenarios)]

    def get_dynamic_story_b_sequence(self, session_state: dict) -> list:
        return self.get_story_b_scenario(session_state)["sequence"]

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
                new_sequence = session_state.get("story_b_sequence", []) + [expected_event["id"]]
                return {"decision": "ADVANCE", "new_sequence": new_sequence, "is_complete": len(new_sequence) >= len(all_events)}
            else:
                return {"decision": "NOT_COMPLETE", "message": "Incorrect or out of order event."}

        return {"decision": "UNCERTAIN"}

evaluator = DeterministicEvaluator()

