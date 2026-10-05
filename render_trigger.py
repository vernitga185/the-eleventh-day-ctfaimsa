import requests
import json

API_KEY = 'rnd_T3DQKBHCV4cHLF3w8X1MvTCd5bCH'
HEADERS = {
    'Authorization': f'Bearer {API_KEY}', 
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

srv_id = 'srv-db19dp6gekts73cqbqag'

# Trigger a new deploy
payload = {"clearCache": "clear"}
res = requests.post(f'https://api.render.com/v1/services/{srv_id}/deploys', headers=HEADERS, json=payload)
print("Deploy Triggered:", res.status_code)
print(json.dumps(res.json(), indent=2))
