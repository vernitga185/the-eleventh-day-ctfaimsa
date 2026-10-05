import requests
import json

API_KEY = 'rnd_T3DQKBHCV4cHLF3w8X1MvTCd5bCH'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'}

srv_id = 'srv-db157j5g1s2s738kb7l0'
res = requests.get(f'https://api.render.com/v1/services/{srv_id}', headers=HEADERS)
print(json.dumps(res.json(), indent=2))
