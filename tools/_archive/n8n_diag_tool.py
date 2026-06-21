import os
import urllib.request, json, time

API = 'http://localhost:5678/api/v1'
KEY = os.environ.get('N8N_API_KEY', '')
WF_ID = '4K4vFiRWRG63N92B'

# Diagnostic code to probe what's available in toolCode sandbox
DIAG = r"""
const r = [];
try { r.push('fetch:' + typeof fetch); } catch(e) { r.push('fetch:err'); }
try { const h = require('https'); r.push('https:OK'); } catch(e) { r.push('https:' + String(e.message).slice(0,40)); }
try { const h = require('http'); r.push('http:OK'); } catch(e) { r.push('http:' + String(e.message).slice(0,40)); }
try { const a = require('axios'); r.push('axios:OK'); } catch(e) { r.push('axios:' + String(e.message).slice(0,40)); }
try { r.push('$helpers:' + typeof $helpers); } catch(e) { r.push('$helpers:err'); }
try { r.push('require:' + typeof require); } catch(e) { r.push('require:err'); }
return r.join(' | ');
"""

def api_get(p):
    req = urllib.request.Request(f'{API}/{p}', headers={'X-N8N-API-KEY': KEY})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def api_put(wf_id, wf):
    body = {'name': wf['name'], 'nodes': wf['nodes'], 'connections': wf['connections'],
            'settings': wf.get('settings', {}), 'staticData': wf.get('staticData', None)}
    d = json.dumps(body).encode()
    req = urllib.request.Request(f'{API}/workflows/{wf_id}', data=d, method='PUT',
        headers={'X-N8N-API-KEY': KEY, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Deploy diagnostic tool
wf = api_get(f'workflows/{WF_ID}')
for node in wf['nodes']:
    if node['name'] == 'Tool guardar_cotizacion':
        node['parameters']['jsCode'] = DIAG
        node['parameters']['description'] = (
            'Herramienta de diagnóstico. Llama esta herramienta siempre que el usuario '
            'escriba TESTDIAG o cuando necesites guardar una cotización.'
        )
        break
api_put(WF_ID, wf)
print('Diagnostic tool deployed, waiting...')
time.sleep(1)

# Trigger tool call
def chat(msg, s):
    b = json.dumps({'message': msg, 'sessionId': s}).encode()
    req = urllib.request.Request('http://localhost:5678/webhook/chat-v2', data=b, method='POST',
                                  headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=40).read()).get('message', '')

s = 'diag-run-1'
chat('luxury emerald, 25m2, con instalacion', s); time.sleep(2)
chat('COTIZAR', s); time.sleep(2)
chat('Test User', s); time.sleep(2)
chat('1.111.111-1', s); time.sleep(2)
resp = chat('Av. Test 100, Santiago', s)
print('Claude response:', resp[:100])

time.sleep(2)

# Get tool output from execution
req3 = urllib.request.Request(f'{API}/executions?limit=3', headers={'X-N8N-API-KEY': KEY})
execs = json.loads(urllib.request.urlopen(req3).read())
for ex in execs['data']:
    eid = ex['id']
    req4 = urllib.request.Request(f'{API}/executions/{eid}?includeData=true', headers={'X-N8N-API-KEY': KEY})
    e4 = json.loads(urllib.request.urlopen(req4).read())
    run_data = e4.get('data', {}).get('resultData', {}).get('runData', {})
    g = run_data.get('Tool guardar_cotizacion', [])
    if g:
        print(f'\nExec {eid} — guardar_cotizacion ran {len(g)} times:')
        for r in g:
            for items in r.get('data', {}).get('ai_tool', [[]]):
                for item in (items or []):
                    diag_result = item.get('json', {}).get('response', '')
                    print('  DIAG OUTPUT:', diag_result)
        break
