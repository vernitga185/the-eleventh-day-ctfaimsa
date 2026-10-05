import json
import logging
from typing import List, Dict, Any
from .config import settings

logger = logging.getLogger(__name__)

EVALUATOR_INSTRUCTIONS = """You are a strict semantic milestone evaluator for a historical reenactment archive.
Your job is to determine if the player and the system have successfully covered the events required for a milestone, based ONLY on the evidence trace provided.

The evaluator trace contains:
- Retrieved source excerpts
- The live conversation context
- Tool calls that recorded actions


Compare the recorded actions against the original source text. 
Does the reenactment faithfully cover the required events for this milestone?

Output ONLY valid JSON matching this schema exactly:
{
  "decision": "COMPLETE | NOT_COMPLETE | UNCERTAIN",
  "covered_events": ["list of events successfully covered"],
  "evidence_source_ids": ["source IDs that justify the decision"],
  "confidence": 0.95
}

Rules:
- Output only JSON matching the schema.
- If uncertain or missing evidence, output UNCERTAIN.
- Do NOT guess. Use only the provided trace.

Reenactment Rules:
- A compound request (e.g. "I cut his bow, standard, banner, charioteer and umbrella") MUST NOT be accepted as completing all events. Each historical action must be a distinguishable, independent event in the trace. If a single trace entry attempts to bundle multiple distinct historical actions, reject it (NOT_COMPLETE) or only credit one.

Story B Rules:
- The canonical event requires three broad-headed shafts targeting BOTH arms AND the head.
- You must NOT return COMPLETE if the trace only shows one arm, or only the head, or fewer than three strikes total. The evidence must explicitly support the full sequence.
"""

class SemanticEvaluator:
    def __init__(self):
        pass
        
    def evaluate_milestone(
        self, 
        llm,
        milestone_question: str, 
        tool_trace: List[Dict[str, Any]], 
        retrieved_passages: List[Dict[str, Any]],
        recent_conversation: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Calls the local model (temperature 0) to evaluate milestone progress.
        """
        if not llm:
            logger.warning("Model not provided to evaluator. Mocking UNCERTAIN.")
            return {"decision": "UNCERTAIN", "covered_events": [], "evidence_source_ids": [], "confidence": 0.0}

        trace_json = json.dumps(tool_trace, indent=2)
        passages_json = json.dumps(retrieved_passages, indent=2)
        convo_json = json.dumps(recent_conversation, indent=2)
        
        user_message = f"""
Milestone Question:
{milestone_question}

Retrieved Canonical Passages:
{passages_json}

Recorded Action Trace:
{trace_json}

Recent Conversation:
{convo_json}
"""
        
        try:
            response = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": EVALUATOR_INSTRUCTIONS},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
                max_tokens=200
            )
            
            output_content = response["choices"][0]["message"].get("content", "{}")
            return json.loads(output_content)
        except Exception as e:
            logger.error(f"Error evaluating milestone: {e}")
            return {
                "decision": "UNCERTAIN",
                "covered_events": [],
                "evidence_source_ids": [],
                "confidence": 0.0
            }

evaluator = SemanticEvaluator()
