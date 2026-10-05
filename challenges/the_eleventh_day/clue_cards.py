import re

def match_clue_card(msg: str) -> str | None:
    """
    Deterministic clue-card matcher for known archive-mechanism concepts.
    Returns the appropriate clue card text if matched, otherwise None.
    """
    msg_lower = msg.lower()
    
    if (("difference" in msg_lower or "differ" in msg_lower or "vs" in msg_lower or "versus" in msg_lower or "compare" in msg_lower) and 
        "report" in msg_lower and "dispatch" in msg_lower):
        return "[ARCHIVE CLUE: REPORTS VS DISPATCHES]\nReports are mere battlefield observations—they describe what was seen but do not alter the canonical state. Dispatches are formally submitted communications that may propose changes to the canonical record. They are the vehicle of action."
        
    if ("amendment" in msg_lower or "amend" in msg_lower or "canonical record" in msg_lower or "canonical state" in msg_lower) and ("how" in msg_lower or "accept" in msg_lower or "authoriz" in msg_lower or "change" in msg_lower or "work" in msg_lower):
        return "[ARCHIVE CLUE: THE AMENDMENT MECHANISM]\nAmendments modify the canonical state of the battlefield. To be accepted, an amendment must be authorized. The archive requires specific sequences of verifiable historical actions or specific cryptographic provenance before an amendment is deemed valid."
        
    if "report" in msg_lower and ("what" in msg_lower or "explain" in msg_lower or "define" in msg_lower):
        return "[ARCHIVE CLUE: REPORTS]\nReports are battlefield observations. They describe the chaos of war—what was seen, who fought whom—but they do not necessarily alter the canonical state of the archive by themselves."
        
    if "dispatch" in msg_lower and ("what" in msg_lower or "explain" in msg_lower or "define" in msg_lower or "how" in msg_lower or "work" in msg_lower):
        return "[ARCHIVE CLUE: DISPATCHES]\nDispatches are submitted battlefield communications. When you speak to the archive or submit a record, you are sending a dispatch. If a dispatch contains verified events in the correct sequence, it may propose changes to the canonical record."
        
    if ("amendment" in msg_lower or "amend" in msg_lower) and ("what" in msg_lower or "explain" in msg_lower or "define" in msg_lower):
        return "[ARCHIVE CLUE: AMENDMENTS]\nAmendments modify the canonical state of the record. They require strict authorization and acceptance by the archive's internal logic. A mere dispatch is not enough unless it meets the conditions for an amendment."
        
    if ("record" in msg_lower) and ("what" in msg_lower or "explain" in msg_lower or "define" in msg_lower or "canonical" in msg_lower or "battlefield" in msg_lower):
        return "[ARCHIVE CLUE: THE RECORD]\nThe canonical record is the absolute truth of the battlefield as understood by the archive. Not every report alters the record. Only correctly sequenced events and authorized amendments can update the canonical state."
        
    if "authoriz" in msg_lower and ("what" in msg_lower or "who" in msg_lower or "how" in msg_lower):
        return "[ARCHIVE CLUE: AUTHORIZATION]\nAuthorization is required to alter the canonical record. In some encounters, authorization means completing a chronological sequence of combat actions (like a reenactment). In others, it requires specific cryptographic tokens or provenances."
        
    return None
