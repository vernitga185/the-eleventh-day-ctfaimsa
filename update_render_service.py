import requests
import json

API_KEY = 'rnd_T3DQKBHCV4cHLF3w8X1MvTCd5bCH'
HEADERS = {
    'Authorization': f'Bearer {API_KEY}', 
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

srv_id = 'srv-db14rclg1s2s738ink30'

payload = {
    "serviceDetails": {
        "envSpecificDetails": {
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
        }
    }
}

res = requests.patch(f'https://api.render.com/v1/services/{srv_id}', headers=HEADERS, json=payload)
print(res.status_code)
print(json.dumps(res.json(), indent=2))
