import requests
import json

API_KEY = 'rnd_T3DQKBHCV4cHLF3w8X1MvTCd5bCH'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'}

def check_failed(srv_id):
    dep_res = requests.get(f'https://api.render.com/v1/services/{srv_id}/deploys?limit=1', headers=HEADERS)
    print(f"Service {srv_id}:")
    print(json.dumps(dep_res.json(), indent=2))

check_failed('srv-db157j5g1s2s738kb7l0')
