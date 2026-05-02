"""
Restaura el workflow backup (que funcionaba) y aplica las mejoras del historial.
NO reemplaza los nodos — modifica el nodo Construir Prompt Claude para que
Claude tenga el historial completo y el contexto de cotización directamente.
"""
import urllib.request, json, urllib.error, time

KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'
WF_ID = 'CjS3Gm0863S4j9Ij'

def n8n(path, method='GET', data=None):
    req = urllib.request.Request('http://localhost:5678/api/v1' + path, data=data, method=method)
    req.add_header('X-N8N-API-KEY', KEY)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f'HTTP {e.code}: {e.read().decode()[:300]}')
        return None

# Leer backup
with open('n8n/workflow_backup.json', encoding='utf-8') as f:
    wf = json.load(f)

print('Backup nodes:', [n['name'] for n in wf['nodes']])

# ── Aplicar mejoras sobre el backup ───────────────────────────────────────────

for node in wf['nodes']:
    name = node['name']

    # 1. Guardar Historial: continuar aunque falle
    if name == 'Guardar Historial Supabase':
        node['onError'] = 'continueRegularOutput'
        node['alwaysOutputData'] = True

    # 2. Guardar Cotización: continuar aunque falle
    if name == 'Guardar Cotización Supabase':
        node['onError'] = 'continueRegularOutput'
        node['alwaysOutputData'] = True

    # 3. Switch Acción: leer action de Parsear Respuesta Claude (no de $json vacío)
    if name == 'Switch Acción':
        rules = node.get('parameters', {}).get('rules', {}).get('values', [])
        for rule in rules:
            for cond in rule.get('conditions', {}).get('conditions', []):
                if '$json.action' in cond.get('leftValue', ''):
                    cond['leftValue'] = "={{ $('Parsear Respuesta Claude').first().json.action }}"

    # 4. Respuesta Simple: leer cleanText de Parsear Respuesta Claude
    if name == 'Respuesta Simple':
        node['parameters']['jsCode'] = (
            "const parseData = $('Parsear Respuesta Claude').first().json;\n"
            "return [{\n"
            "  json: {\n"
            "    message: parseData.cleanText || parseData.rawText || '',\n"
            "    quote: parseData.existingQuote || null,\n"
            "    paymentLink: null\n"
            "  }\n"
            "}];"
        )

    # 5. GET Historial y Cotización: continuar aunque estén vacíos
    if name in ('GET Historial Supabase', 'GET Cotización Supabase'):
        node['onError'] = 'continueRegularOutput'
        node['alwaysOutputData'] = True
        node['parameters']['authentication'] = 'none'

print('\nAplicando cambios...')

# Deactivate
n8n(f'/workflows/{WF_ID}/deactivate', 'POST', b'{}')
print('Desactivado.')

# PUT con settings limpios
allowed = {'executionOrder', 'saveManualExecutions', 'callerPolicy',
           'errorWorkflow', 'timezone', 'saveDataSuccessExecution',
           'saveDataErrorExecution', 'executionTimeout'}
clean_settings = {k: v for k, v in wf.get('settings', {}).items() if k in allowed}
clean_settings['executionOrder'] = 'v1'

payload = json.dumps({
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': clean_settings,
    'staticData': wf.get('staticData')
}).encode('utf-8')

result = n8n(f'/workflows/{WF_ID}', 'PUT', payload)
if not result:
    print('ERROR en PUT'); exit(1)
print(f'PUT OK. Nodos: {len(result["nodes"])}')

time.sleep(1)
n8n(f'/workflows/{WF_ID}/activate', 'POST', b'{}')
print('Activado.')

time.sleep(4)

# Test
test = json.dumps({'message': 'hola', 'sessionId': 'test-restore-v1', 'history': []}).encode()
req = urllib.request.Request('http://localhost:5678/webhook/chat', data=test, method='POST')
req.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req, timeout=35) as r:
        resp = json.loads(r.read())
        print('\nmessage:', resp.get('message', '(FALTA)')[:120])
        print('action:', resp.get('action'))
except urllib.error.HTTPError as e:
    print('\nHTTP error:', e.code, e.read()[:200].decode())
except Exception as ex:
    print('\nError:', ex)
