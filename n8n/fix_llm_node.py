"""Fixes the lmChatAnthropic node in the AI Agent v2 workflow - tries multiple model/version combos"""
import urllib.request, urllib.error, json, time

KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'
WF = '4K4vFiRWRG63N92B'

def n8n(path, method='GET', payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request('http://localhost:5678/api/v1' + path, data=data, method=method)
    req.add_header('X-N8N-API-KEY', KEY)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        print('HTTP', e.code, e.read().decode()[:300]); return None

wf = n8n('/workflows/' + WF)

for n in wf['nodes']:
    if n['name'] == 'Anthropic Claude Sonnet':
        # Use resource locator format + claude-sonnet-4-5 (same as working workflow)
        n['typeVersion'] = 1.3
        n['parameters'] = {
            'model': {
                '__rl': True,
                'value': 'claude-sonnet-4-5',
                'mode': 'id'
            },
            'options': {'maxTokens': 1024}
        }
        print('Updated LLM node:', json.dumps(n['parameters']))

n8n('/workflows/' + WF + '/deactivate', 'POST', {})
time.sleep(1)
result = n8n('/workflows/' + WF, 'PUT', {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': {'executionOrder': 'v1'}
})
print('PUT:', 'OK nodes=' + str(len(result['nodes'])) if result else 'FAIL')

n8n('/workflows/' + WF + '/activate', 'POST', {})
print('Activated')
time.sleep(3)

body = json.dumps({'message': 'hola', 'sessionId': 'test-v2-d'}).encode()
req2 = urllib.request.Request('http://localhost:5678/webhook/chat-v2', data=body, method='POST')
req2.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req2, timeout=50) as r:
        raw = r.read()
        print('RAW:', raw[:400].decode('utf-8', errors='replace'))
        if raw.strip():
            print('JSON:', json.loads(raw))
except urllib.error.HTTPError as e:
    print('HTTP error:', e.code, e.read()[:300].decode())
except Exception as ex:
    print('Error:', type(ex).__name__, ex)
