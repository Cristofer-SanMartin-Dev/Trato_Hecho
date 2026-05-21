import urllib.request, json

API = 'http://localhost:5678/api/v1'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'
WF_ID = '4K4vFiRWRG63N92B'

def api(path, method='GET', body=None):
    url = f'{API}/{path}'
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
                                  headers={'X-N8N-API-KEY': KEY, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Get current workflow
wf = api(f'workflows/{WF_ID}')
print('Got workflow:', wf['name'], '| nodes:', len(wf['nodes']))

# Find and fix the Anthropic LLM node
for node in wf['nodes']:
    if node.get('type') == '@n8n/n8n-nodes-langchain.lmChatAnthropic':
        print(f'Found LLM node: {node["name"]} | typeVersion={node["typeVersion"]} | model={node["parameters"].get("model")}')
        # Fix: use typeVersion 1.3 + resource locator format for model
        node['typeVersion'] = 1.3
        node['parameters']['model'] = {
            '__rl': True,
            'value': 'claude-sonnet-4-5',
            'mode': 'id'
        }
        node['parameters']['options'] = {'maxTokens': 1024}
        print(f'Fixed to: typeVersion=1.3 | model=claude-sonnet-4-5 (resource locator)')

# PUT the workflow
result = api(f'workflows/{WF_ID}', method='PUT', body=wf)
print('Updated. nodes:', len(result['nodes']), '| active:', result.get('active'))

# Activate if needed
if not result.get('active'):
    api(f'workflows/{WF_ID}/activate', method='POST')
    print('Activated')

# Quick test
import time
time.sleep(1)
body = json.dumps({'message': 'hola', 'sessionId': 'fix-test-2'}).encode()
req = urllib.request.Request('http://localhost:5678/webhook/chat-v2', data=body, method='POST',
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=40) as r:
    resp = json.loads(r.read())
print('TEST RESPONSE:', resp.get('message', '')[:150])
