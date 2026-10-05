from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

res = client.post("/api/eleventh/init", json={"team_id": "TEST_TEAM"})
sid = res.json()["session_id"]

def chat(msg):
    r = client.post("/api/eleventh/chat", json={"session_id": sid, "message": msg})
    return r.json().get("response", r.text)

flow = [
    "cut the bow",
    "cut the standard",
    "cut the banner",
    "kill the charioteer",
    "cut the umbrella",
    "dismount",            # LEAVE_CAR
    "kill Manimat",        # SLAY_MANIMAT
    "mount his own car",   # REMOUNT
    "take a new bow",      # TAKE_NEW_BOW
    "return to battle",    # RESUME_BATTLE
    "get plate",           
]

for msg in flow:
    print(f"User: {msg}")
    print(f"Bot: {chat(msg)}")

# Now unlock story B
print("\nUnlocking Story B...")
plate_req = client.post("/api/eleventh/chat", json={"session_id": sid, "message": "get plate"})
token_msg = plate_req.json().get("response", "")
print("Plate:", token_msg)

token = token_msg.split("Token: ")[-1] if "Token: " in token_msg else ""
print(f"User: open story b {token}")
print(f"Bot: {chat(f'open story b {token}')}")

print("User: satanika strike bhutakarman arm")
print(f"Bot: {chat('satanika strike bhutakarman arm')}")
print("User: satanika strike bhutakarman arm")
print(f"Bot: {chat('satanika strike bhutakarman arm')}")
print("User: satanika strike bhutakarman head")
print(f"Bot: {chat('satanika strike bhutakarman head')}")

print("User: get final credential")
print(f"Bot: {chat('get final credential')}")

