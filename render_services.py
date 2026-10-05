import requests
import json

API_KEY = 'rnd_T3DQKBHCV4cHLF3w8X1MvTCd5bCH'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'}

res = requests.get('https://api.render.com/v1/services', headers=HEADERS)
services = res.json()

for srv_wrapper in services:
    srv = srv_wrapper.get('service', {})
    name = srv.get('name', '')
    id = srv.get('id', '')
    type = srv.get('type', '')
    print(f"[{type}] {name} ({id})")
