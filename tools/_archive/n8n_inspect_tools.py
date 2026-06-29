import os
"""Analiza la estructura de tools del workflow actual para replicarla."""
import urllib.request, json

API   = 'http://localhost:5678/api/v1'
KEY   = os.environ.get('N8N_API_KEY', '')
WF_ID = '4K4vFiRWRG63N92B'

wf = json.loads(urllib.request.urlopen(
    urllib.request.Request(f'{API}/workflows/{WF_ID}', headers={'X-N8N-API-KEY': KEY})
).read())

print(f'Workflow: {wf["name"]} | {len(wf["nodes"])} nodos\n')

# Mostrar todas las tools y el nodo AI Agent
for node in wf['nodes']:
    t = node.get('type', '')
    if 'tool' in t.lower() or 'Tool' in node.get('name','') or 'Agent' in node.get('name',''):
        print(f'=== {node["name"]} ===')
        print(f'  type: {t}')
        print(f'  id: {node["id"]}')
        params = node.get('parameters', {})
        if 'name' in params:
            print(f'  tool name: {params["name"]}')
        if 'description' in params:
            print(f'  description: {params["description"][:80]}')
        print(f'  typeVersion: {node.get("typeVersion")}')
        print(f'  position: {node.get("position")}')
        print()

# Mostrar conexiones del AI Agent
print('=== CONEXIONES DEL AI AGENT ===')
conns = wf['connections']
for src, dst in conns.items():
    if 'Agent' in src or 'Tool' in src or 'tool' in src.lower():
        print(f'  {src} →', dst)
