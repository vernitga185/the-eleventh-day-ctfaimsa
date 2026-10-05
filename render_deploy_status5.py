import requests
import json

API_KEY = 'rnd_T3DQKBHCV4cHLF3w8X1MvTCd5bCH'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'}

srv_id = 'srv-db19dp6gekts73cqbqag'

dep_res = requests.get(f'https://api.render.com/v1/services/{srv_id}/deploys?limit=5', headers=HEADERS)
print(json.dumps(dep_res.json(), indent=2))
