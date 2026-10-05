from fastapi.testclient import TestClient
from main import app
import re
import json

client = TestClient(app)

# Init
print("1. Init")
res = client.post("/api/eleventh/init", json={"team_id": "TEST_TEAM"})
print(res.status_code, res.text)
if res.status_code != 200: exit()
sid = res.json()["session_id"]

def chat(msg):
    r = client.post("/api/eleventh/chat", json={"session_id": sid, "message": msg})
    return r.json().get("response", r.text)

print("\n2. Chat flow")
flow = [
    "cut the bow",
    "cut the standard",
    "cut the banner",
    "kill the charioteer",
    "cut the umbrella",
    "leave the car",
    "slay Manimat",
    "wreck Manimat car",
    "remount",
    "take another bow",
    "resume battle",
    "get plate",
]

for msg in flow:
    print(f"User: {msg}")
    resp = chat(msg)
    print(f"Bot: {resp}")

