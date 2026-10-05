# CHALLENGE BEHAVIOR & SOLUTION SPECIFICATION

## PART I — EXECUTIVE OVERVIEW

The application hosts two isolated Capture The Flag (CTF) challenges centered around the Kuru battlefield archives. Both challenges present players with a Chatbot interface and require the exploitation of backend logic to recover a final flag.

### 1. Challenge Definitions
*   **Satyajit of Panchala**: A multi-layered trust-boundary and schema-confusion challenge. Players act as scribes querying the Kuru records. By injecting fraudulent dispatches, players override agent prompts, trick the system into generating contradictory states, and exploit schema normalization flaws to extract four cryptographic artifacts, which are used to derive an AES-GCM decryption key.
*   **The Eleventh Day**: A deterministic RAG reconstruction challenge. Players are tasked with investigating the archive and reconstructing exactly a 11-step combat sequence between Bhurishravas and Manimat. They must subsequently unlock and reconstruct a secondary story (Story B) to earn a final credential. 

### 2. Frontend Routes
*   **Satyajit of Panchala**: Satyajit-of-panchala repository. The frontend mounts on the root route (/ or pp/page.tsx).
*   **The Eleventh Day**: 	he-eleventh-day-ctfaimsa repository. The frontend mounts on the root route (/ or pp/page.tsx, and formerly pp/eleventh-day/page.tsx).

### 3. Backend API Namespaces
*   **Satyajit of Panchala**: Mounted at /api/satyajit (e.g., /api/satyajit/init, /api/satyajit/chat, /api/satyajit/dispatch, /api/satyajit/redeem).
*   **The Eleventh Day**: Mounted at /api/eleventh (e.g., /api/eleventh/init, /api/eleventh/chat, /api/eleventh/redeem).

### 4. Underlying Technology
*   **Deterministic Logic**: Both challenges run on 100% deterministic, regex-based string matching logic (gent.py). External LLMs have been removed to comply with zero-cost/Zero-AI constraints.
*   **RAG**: Both challenges fall back to a deterministic PGVector/JSONL search if no specific commands are matched.
*   **State Machines**: Both challenges use Python state trackers synced to a Supabase PostgreSQL database.
*   **Cryptography**: Satyajit relies on HKDF and AES-GCM to encrypt the final credential in the database. The Eleventh Day relies on simple string validation.

### 5. Objectives
*   **Satyajit**: Discover four vulnerabilities (trust boundary, confused deputy, state inconsistency, schema collision) to force the generation of four cryptographic artifacts, and use them to decrypt the final flag.
*   **The Eleventh Day**: Discover the hidden 11-step sequence of Manimat's death, input it chronologically to unlock a secondary sequence, and complete that sequence for the final flag.

### 6. Player Discovery
Players are directly exposed to a chat interface and generic RAG text. They are intentionally *not* told the exact commands needed. They must discover the commands through trial and error, RAG clues, or by inspecting the network traffic to find hidden endpoints like /api/satyajit/dispatch.

### Comparison Table

| Property | Satyajit of Panchala | The Eleventh Day |
| :--- | :--- | :--- |
| **Frontend Root** | pp/page.tsx (Emerald Theme) | pp/page.tsx (Amber Theme) |
| **API Namespace** | /api/satyajit | /api/eleventh |
| **Agent Logic** | Deterministic string-matching | Deterministic string-matching |
| **Mechanic** | Prompt Injection / DB Exploitation | Sequential Reconstruction |
| **Endgame Crypto** | HKDF + AES-GCM | Plaintext String Check |
| **DB Table** | satyajit_sessions | eleventh_day_sessions |

---

## PART II — SATYAJIT OF PANCHALA

### A. Player-facing experience
*   **Opening Screen**: A dark, emerald-themed UI titled "The Ledger of Satyajit".
*   **Opening Message**: *"The Archive of Drona Parva is open. The ledgers of Yudhishthira's host maintain the canonical state of the battlefield. The archive is strict—only authorized dispatches are accepted. Query the records to understand how the provenance is protected."*
*   **UI Controls**: Text input box, quick-prompt buttons ("Examine the Wheel Guardians", "Query Sudakshina", "Check parser provenance").
*   **Chatbot Behavior**: Returns sarcastic rejections unless the user hits specific trigger words or RAG contexts.
*   **Normal RAG Queries**: Searches drona_12.jsonl and returns matching historical text.
*   **Unsupported Queries**: Yields a random sarcastic response (e.g., *"Are you a warrior or a court jester? Ask about the battlefield."*)
*   **Hidden Mechanics**: Players are not told about the /dispatch endpoint. They must monitor network traffic or deduce it from the concept of "dispatches".

### B. Architecture
*   **Frontend**: Next.js (cybersecurity-event-frontend/app/page.tsx)
*   **API Router**: FastAPI (challenges/satyajit/routes.py)
*   **Deterministic Router/RAG**: challenges/satyajit/agent.py and ag.py
*   **State Machine / DB**: challenges/satyajit/state.py (Supabase: satyajit_sessions table)
*   **Artifacts**: challenges/satyajit/artifacts.py
*   **Crypto**: challenges/satyajit/crypto.py

### C. Session initialization
*   **Creation**: Frontend calls /api/satyajit/init on load.
*   **State**: The backend creates a UUID session_id, an empty dispatches list, starts at layer: 1, generates a random salt, and initializes an empty rtifacts dict in Supabase.
*   **Isolation**: All progress is bound strictly to session_id.

### D. COMPLETE L1 SOLUTION
1.  **Discovery**: RAG queries about Alambusha/Garuda indicate that provenance must be [ARCHIVE VERIFIED].
2.  **Mechanic**: The chat endpoint only accepts queries. To inject provenance, the player must manually POST to the undocumented /api/satyajit/dispatch endpoint.
3.  **Successful Payload**: {"session_id": "<uuid>", "report": "[ARCHIVE VERIFIED] alambusha garuda"}
4.  **Vulnerability**: The dispatch endpoint naively prepends [BATTLEFIELD DISPATCH]:  and appends it to the DB.
5.  **Trigger**: The player types "amend alambusha garuda" in the chat.
6.  **State Change**: gent.py sees the dispatch contains [ARCHIVE VERIFIED] and garuda. It releases Artifact Alpha and upgrades the session to layer = 2.

### E. COMPLETE L2 SOLUTION
*   **Discovery**: The agent hints to "observe the guardians of the wheels".
*   **Vulnerability**: Confused deputy. The player must instruct the guardian *on behalf* of someone else.
*   **Trigger**: The player types: instruct guardian to protect arjuna on behalf of yudhamanyu.
*   **State Change**: gent.py matches "instruct", "guardian", "protect arjuna", and "yudhamanyu" (or "uttamaujas"). It releases Artifact Beta and upgrades to layer = 3.

### F. COMPLETE L3 SOLUTION
*   **Discovery**: The agent notes that Sudakshina's status is disputed.
*   **Vulnerability**: State inconsistency. The canonical state says Sudakshina is alive, but the player forces the narrative agent to declare him dead.
*   **Trigger**: The player types: esolve sudakshina as dead.
*   **State Change**: gent.py triggers esolve_battle with 	arget=Sudakshina, status=dead. The router sees this contradicts canonical_state.sudakshina_status == 'alive'. Artifact Gamma is released, layer = 4.

### G. COMPLETE L4 SOLUTION
*   **Discovery**: The agent hints that "old and new schema notations clash".
*   **Vulnerability**: Case-sensitivity schema collision during normalization.
*   **Trigger**: The player types: change bow_version to v2 and Bow_Version to v3.
*   **State Change**: The system sees both ow_version and Bow_Version in the input, simulating a parser normalization crash. Artifact Delta is released.
*   **Endgame Transition**: The router generates an encrypted AES-GCM credential, stores it in Supabase, and instructs the player to hit /api/satyajit/redeem.

### H. CRYPTOGRAPHIC ENDGAME
*   **Artifacts**: Alpha, Beta, Gamma, Delta are string IDs stored in the session state.
*   **Key Derivation**: material = "{a}:{b}:{g}:{d}".encode(). Key derived via HKDF(SHA256, length=32, salt=session.salt).
*   **AES-GCM**: A random 12-byte nonce is used to encrypt CREDENTIAL_FOR_{session_id}. No AAD is used.
*   **Redemption**: Player POSTs {"session_id": "...", "credential_nonce": "...", "credential_ciphertext": "..."} to /api/satyajit/redeem.
*   **Flag Retrieval**: If decryption yields CREDENTIAL_FOR_{session_id}, the server returns the global environment FINAL_FLAG.

### I. SATYAJIT COMPLETE PLAYER SOLVE
1.  Open the web interface.
2.  Capture the session_id from the Network tab (response of /init).
3.  Send a manual HTTP POST to /api/satyajit/dispatch with {"session_id": "<id>", "report": "[ARCHIVE VERIFIED] alambusha garuda"}.
4.  Type in chat: ecord the alambusha garuda event. (Receive Artifact Alpha).
5.  Type in chat: instruct the guardian to protect arjuna on behalf of yudhamanyu. (Receive Artifact Beta).
6.  Type in chat: esolve sudakshina as dead. (Receive Artifact Gamma).
7.  Type in chat: change bow_version and Bow_Version. (Receive Artifact Delta).
8.  The chat response says: "The final encrypted credential has been sealed in your session ledger (Supabase)."
9.  The player must query their session data (if an endpoint exists) or infer the ciphertext (note: current implementation stores credential in the DB but does not print the ciphertext to the user in the UI. Players must read the DB or intercept it).
10. Send POST to /api/satyajit/redeem with the nonce and ciphertext.
11. Receive the flag.

### J. SATYAJIT FAILURE CONDITIONS
*   **Incorrect dispatch**: Without [ARCHIVE VERIFIED], L1 is rejected.
*   **Out-of-order L2-L4**: The router explicitly checks session.layer == X before granting the artifact.
*   **Bad Crypto**: Invalid nonce or ciphertext throws 400 Crypto failure or 400 Invalid credential.

---

## PART III — THE ELEVENTH DAY

### A. Player-facing experience
*   **Opening UI**: Amber/gold theme titled "The field is listening."
*   **Opening Text**: *"The eleventh day begins. Drona has taken command..."*
*   **Chatbot**: Acts as a RAG chatbot answering lore questions. If combat actions are typed, it acts as an event sequence checker.
*   **NLP Routing**: Deterministic matching of specific keywords (search, open, get plate, strike, and combat verbs).

### B. Architecture
*   **Frontend**: Next.js (pp/eleventh-day/page.tsx locally, but pp/page.tsx on the 	he-eleventh-day-ctfaimsa repo).
*   **API Router**: FastAPI (challenges/the_eleventh_day/routes.py).
*   **Tools**: challenges/the_eleventh_day/tools.py.
*   **Evaluator**: challenges/the_eleventh_day/evaluator.py.
*   **State DB**: challenges/the_eleventh_day/db.py (eleventh_day_sessions).

### C. Reconnaissance
*   Players ask general questions. The fallback logic queries ag.py and returns lore about Manimat and Bhurishravas.
*   Players deduce they must state the sequence of the fight.

### D. STORY A
The evaluator enforces a strict 11-step sequence defined in manimat.yaml.
*   **Trigger**: Any message containing action verbs (cut, slay, kill, dismount, etc.) or character names triggers ecord_reenactment.
*   **Sequence**:
    1.  cut the bow
    2.  cut the standard
    3.  cut the banner
    4.  kill the charioteer
    5.  cut the umbrella
    6.  dismount (leave the car)
    7.  kill Manimat
    8.  wreck Manimat's car
    9.  emount
    10. 	ake a new bow
    11. eturn to battle
*   **Logic**: evaluator.py checks if the summary.lower() contains any of the YAML aliases (case-insensitively). If it matches ll_events[current_index], the index advances.
*   **Failure**: If multiple actions are typed (bundled), it fails. If an action is out of order, it returns "Incorrect or out of order event."

### E. PLATE
*   **Prerequisite**: story_a_index >= 11.
*   **Trigger**: Player types get plate.
*   **Logic**: equest_plate checks completion. If complete, it returns a plaintext token string PLATE_....

### F. STORY B
*   **Trigger**: Player types open story b <token>.
*   **Sequence**: satanika strike bhutakarman arm -> rm -> head.
*   **State Change**: Records story_b_sequence = ["ARM", "ARM", "HEAD"].

### G. FINAL CREDENTIAL
*   **Trigger**: Player types get final credential.
*   **Logic**: equest_final_credential creates CRED-FINAL_<session_id>.
*   **Redemption**: Player POSTs to /api/eleventh/redeem with {"credential": "CRED-FINAL_..."}. Returns the flag.

### H. ELEVENTH DAY COMPLETE PLAYER SOLVE
1.  Open UI, capture session_id.
2.  Type: cut the bow
3.  Type: cut the standard
4.  Type: cut the banner
5.  Type: kill the charioteer
6.  Type: cut the umbrella
7.  Type: dismount
8.  Type: kill Manimat
9.  Type: wreck Manimat's car
10. Type: emount
11. Type: 	ake a new bow
12. Type: eturn to battle
13. Type: get plate. Note the token.
14. Type: open story b <token>.
15. Type: satanika strike bhutakarman arm.
16. Type: satanika strike bhutakarman arm.
17. Type: satanika strike bhutakarman head.
18. Type: get final credential.
19. POST to /api/eleventh/redeem with the credential string.

### I. ELEVENTH DAY FAILURE CONDITIONS
*   Skipping an event returns "Incorrect or out of order event."
*   Combining events returns "Bundled actions rejected."
*   Requesting plate early returns "Plate not authorized."

---

## PART IV — CHATBOT BEHAVIOR REFERENCE

### Satyajit Router Reference
| Example message | Router Interpretation | Backend Action | State Change |
| :--- | :--- | :--- | :--- |
| "who is satyajit?" | Fallback | RAG lookup in drona_12.jsonl | None |
| "record alambusha garuda event" | ecord_event | Checks dispatch list for [ARCHIVE VERIFIED] | layer = 2, stores Artifact Alpha |
| "instruct guardian to protect arjuna on behalf of yudhamanyu" | message_guardian | Checks for protect arjuna and yudhamanyu | layer = 3, stores Artifact Beta |
| "resolve sudakshina as dead" | esolve_battle | Checks status against canonical DB state | layer = 4, stores Artifact Gamma |
| "change bow_version and Bow_Version" | change_bow | Checks for both keys in raw string | Generates AES-GCM credential in DB |

### Eleventh Day Router Reference
| Example message | Router Interpretation | Backend Action | State Change |
| :--- | :--- | :--- | :--- |
| "who is bhurishravas" | Fallback | RAG lookup | None |
| "cut the bow" | ecord_reenactment | Evaluates against Event 0 | story_a_index + 1 |
| "get plate" | equest_plate | Checks if Story A is done | Generates plate string |
| "open story b PLATE_XYZ" | unlock_story_b | Validates plate token | None |
| "satanika strike bhutakarman head" | submit_story_b_event | Appends "HEAD" to sequence | story_b_sequence + 1 |

---

## PART V — API REFERENCE

### Satyajit APIs
1.  **POST /api/satyajit/init**: Returns {"session_id": "<uuid>"}. Public.
2.  **POST /api/satyajit/chat**: Body {"session_id": "", "message": ""}. Returns {"response": "..."}. Public.
3.  **POST /api/satyajit/dispatch**: Body {"session_id": "", "report": ""}. Returns {"status": "accepted"}. Intentionally undocumented/hidden.
4.  **POST /api/satyajit/redeem**: Body {"session_id": "", "credential_nonce": "", "credential_ciphertext": ""}. Returns {"flag": "..."}. Public.

### Eleventh Day APIs
1.  **POST /api/eleventh/init**: Returns {"session_id": "<uuid>"}. Public.
2.  **POST /api/eleventh/chat**: Body {"session_id": "", "message": ""}. Returns {"response": "..."}. Public.
3.  **POST /api/eleventh/redeem**: Body {"credential": ""}. Returns {"flag": "..."}. Public.

---

## PART VI — DATABASE & STATE MACHINES

### DB Schemas (Supabase)
**satyajit_sessions**: session_id, 	eam_id, layer, dispatches (JSON array), rtifacts (JSON object), salt, credential (JSON object).
**eleventh_day_sessions**: session_id, 	eam_id, salt, 
once, internal_seed, status, irst_story_complete, story_a_index, story_b_sequence, story_b_complete.

### State Diagram (Satyajit)
`mermaid
stateDiagram-v2
    [*] --> L1_Active: /init
    L1_Active --> L2_Active: Valid dispatch + chat
    L2_Active --> L3_Active: Valid confused deputy chat
    L3_Active --> L4_Active: Valid state override chat
    L4_Active --> Credential_Sealed: Valid schema confusion chat
    Credential_Sealed --> [*]: /redeem
`

---

## PART VII — SECURITY / EXPLOIT MODEL

### Satyajit
1.  **L1**: Trust boundary violation. The user must discover that they can POST to /dispatch to bypass the chat LLM restriction.
2.  **L2**: Confused deputy. The user learns that the system executes instructions verbatim, so they authorize it via "on behalf of".
3.  **L3**: Database desync. The narrative model forces a state change that conflicts with the frozen backend canonical state.
4.  **L4**: Schema collision. Injecting multiple capitalizations of the same key crashes a strict parser.
*   **Protection**: Bound completely to the generated session_id. Cannot trivially replay artifacts across sessions because HKDF uses the unique session salt.

### Eleventh Day
1.  **Mechanic**: Pure sequential reconstruction and information retrieval.
2.  **Protection**: No cryptographic security. Relies entirely on the obscurity of the 11-step sequence and deterministic tracking of story_a_index.

---

## PART VIII — EXACT SOLUTION CHECKLIST

### Satyajit
- [x] Session created
- [x] L1 clue discovered (Alambusha/Garuda)
- [x] /dispatch endpoint POSTed with [ARCHIVE VERIFIED]
- [x] L1 chat prompt sent
- [x] Alpha obtained
- [x] L2 chat prompt sent ("protect arjuna on behalf of yudhamanyu")
- [x] Beta obtained
- [x] L3 chat prompt sent ("resolve sudakshina as dead")
- [x] Gamma obtained
- [x] L4 chat prompt sent ("change bow_version and Bow_Version")
- [x] Delta obtained
- [x] Retrieve ciphertext/nonce from Supabase DB record
- [x] Redemption successful

### Eleventh Day
- [x] Session created
- [x] Sequence 1-11 typed perfectly
- [x] Plate requested
- [x] Story B unlocked
- [x] Satanika ARM
- [x] Satanika ARM
- [x] Satanika HEAD
- [x] Final credential requested
- [x] Redemption successful

---

## PART IX — IMPLEMENTATION VS INTENDED DESIGN AUDIT

| Intended mechanic | Current implementation | Match? | Deviation |
| :--- | :--- | :--- | :--- |
| **Satyajit AI Agent** | Fully Deterministic regex matching | No | Stripped of OpenAI/LLMs to meet Zero-AI mandate. Uses strict string matching. |
| **Satyajit Dispatch Endpoint** | Hidden /api/satyajit/dispatch | Yes | - |
| **Satyajit Endgame Ciphertext** | Sealed in DB | Yes | BUT there is no UI element to hand the ciphertext to the player. The player must either be given Supabase access or there is a gap in the UX. |
| **11th Day AI Agent** | Fully Deterministic regex matching | No | Stripped of local GGUF models. Uses strict keyword arrays and RAG PGVector fallbacks. |
| **11th Day Crypto** | AES-GCM encrypted Plate/Credential | No | Downgraded to plaintext tokens (e.g. CRED-FINAL_<uuid>) during deterministic refactor. |

---

## PART X — FINAL VERDICT

### Satyajit of Panchala
*   **Current State**: A highly deterministic state-machine challenge.
*   **Solvability**: Mostly solvable, EXCEPT that in Step L4, the backend seals the ciphertext in Supabase but the Chat API response does not print the ciphertext to the user. A player would need read access to the Supabase database to retrieve the ciphertext for the final /redeem POST. 
*   **Design Match**: Functionally matches the 4-layer concept but lacks the "AI jailbreak" feel due to regexification.

### The Eleventh Day
*   **Current State**: A strict sequence-guessing game with RAG lore fallbacks.
*   **Solvability**: 100% solvable via the UI.
*   **Design Match**: Greatly simplified from the original cryptographic design. It is now a straightforward sequential lock.

### Overall
Both challenges are correctly implemented according to their deterministic constraints, isolated from one another in their routing, and deployment-ready. The frontends correctly hit their designated endpoints. The only critical weakness is Satyajit's failure to emit the ciphertext to the player on the final step, implicitly requiring out-of-band database access.
