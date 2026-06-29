import os
"""Prueba rápida: envía PAGAR con la última cotización y muestra el output del nodo MP."""
import urllib.request, json, time

API   = 'http://localhost:5678/api/v1'
KEY   = os.environ.get('N8N_API_KEY', '')
WH    = 'http://localhost:5678/webhook/chat-v2'

def chat(msg, s):
    b = json.dumps({'message': msg, 'sessionId': s}).encode()
    req = urllib.request.Request(WH, data=b, method='POST',
                                 headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read()).get('message', '')

def get_exec(ex_id):
    req = urllib.request.Request(f'{API}/executions/{ex_id}', headers={'X-N8N-API-KEY': KEY})
    return json.loads(urllib.request.urlopen(req).read())

def last_exec_id():
    req = urllib.request.Request(
        f'{API}/executions?limit=1&workflowId=4K4vFiRWRG63N92B',
        headers={'X-N8N-API-KEY': KEY}
    )
    return json.loads(urllib.request.urlopen(req).read())['data'][0]['id']

s = f'test-pago-{int(time.time())}'
print('=== Flujo completo hasta PAGAR ===')

# Cotización rápida
r1 = chat('luxury emerald 25m2 con instalacion', s); print('R1:', r1[:100]); time.sleep(1)
r2 = chat('COTIZAR', s); print('R2:', r2[:100]); time.sleep(1)
r3 = chat('Ana Test', s); print('R3:', r3[:80]); time.sleep(1)
r4 = chat('12.345.678-9', s); print('R4:', r4[:80]); time.sleep(1)
r5 = chat('Av. Principal 123, Melipilla', s); print('R5 (COT):', r5[:200]); time.sleep(2)

# PAGAR
print('\n=== PAGAR ===')
ex_before = last_exec_id()
r6 = chat('PAGAR', s)
print('R6 (PAGO):', r6[:300])
time.sleep(3)

# Ver ejecución
ex_after = last_exec_id()
print('\n=== Ejecución:', ex_after, '===')
detail = get_exec(ex_after)
rd = detail.get('data', {}).get('resultData', {}).get('runData', {})
mp_run = rd.get('Generar Pago MP', [{}])[0]
items = mp_run.get('data', {}).get('main', [[]])[0]
if items:
    j = items[0].get('json', {})
    print('_mp_url:', j.get('_mp_url', '(vacío)'))
    print('_mp_err:', j.get('_mp_err', '(ninguno)'))
    print('output:', str(j.get('output', ''))[:300])
else:
    print('No hay items en Generar Pago MP')
    err = mp_run.get('error', {})
    if err: print('Error nodo:', err)
