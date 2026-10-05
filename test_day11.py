from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

res = client.post("/api/eleventh/init", json={"team_id": "TEST_TEAM"})
sid = res.json()["session_id"]

def chat(msg):
    r = client.post("/api/eleventh/chat", json={"session_id": sid, "message": msg})
    return r.json().get("response", r.text)

flow1 = [
    "drona assumes command",
    "capture yudhishthira alive",
    "arjuna protects him",
    "draw arjuna away",
    "yudhishthira learns of the plan",
    "yudhishthira asks arjuna to protect him",
]

print("Phase 1:")
for msg in flow1:
    print(f"U: {msg}\nB: {chat(msg)}\n")

plate_req = client.post("/api/eleventh/chat", json={"session_id": sid, "message": "get plate"})
token_msg = plate_req.json().get("response", "")
print("Plate:", token_msg)

token = token_msg.split("Token: ")[-1] if "Token: " in token_msg else ""
chat(f"open story b {token}")

flow2 = [
    "arjuna assures protection",
    "drona attacks",
    "arjuna intervenes"
]

print("\nPhase 2:")
for msg in flow2:
    print(f"U: {msg}\nB: {chat(msg)}\n")

print(chat("get final credential"))
