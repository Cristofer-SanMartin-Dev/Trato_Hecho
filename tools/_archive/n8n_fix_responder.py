import os
import urllib.request, json, urllib.error, time

KEY = os.environ.get('N8N_API_KEY', '')
WF  = 'CjS3Gm0863S4j9Ij'

def n8n(path, method='GET', data=None):
    req = urllib.request.Request('http://localhost:5678/api/v1' + path, data=data, method=method)
    req.add_header('X-N8N-API-KEY', KEY)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print('HTTP', e.code, e.read().decode()[:300])
        return None

# Get workflow
wf = n8n(f'/workflows/{WF}')
print('Nodes:', [n['name'] for n in wf['nodes']])

# Fix respondToWebhook — usar JSON.stringify con referencia a Parsear Respuesta
# La expresión n8n usa $() para referenciar nodos por nombre
response_body_expr = (
    "={{ JSON.stringify({ "
    "message: $(\"Parsear Respuesta\").first().json.cleanText || '', "
    "action: $(\"Parsear Respuesta\").first().json.action || 'CHAT', "
    "actionData: $(\"Parsear Respuesta\").first().json.actionData || {}, "
    "quote: null, "
    "paymentLink: null "
    "}) }}"
)

for node in wf['nodes']:
    if node['name'] == 'Responder Webhook':
        node['parameters'] = {
            'respondWith': 'json',
            'responseBody': response_body_expr
        }
        node['typeVersion'] = 1.1
        print('Responder Webhook actualizado')

# Deactivate
n8n(f'/workflows/{WF}/deactivate', 'POST', b'{}')
print('Desactivado')

# PUT
payload = json.dumps({
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': {'executionOrder': 'v1'}
}).encode('utf-8')

result = n8n(f'/workflows/{WF}', 'PUT', payload)
if result:
    print('PUT OK, nodos:', len(result['nodes']))
else:
    print('ERROR en PUT')
    exit(1)

# Activate
n8n(f'/workflows/{WF}/activate', 'POST', b'{}')
print('Activado')

time.sleep(3)

# Test
test = json.dumps({'message': 'hola', 'sessionId': 'test-v5', 'history': []}).encode()
req2 = urllib.request.Request('http://localhost:5678/webhook/chat', data=test, method='POST')
req2.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req2, timeout=35) as r2:
        resp = json.loads(r2.read())
        print('message:', resp.get('message', '(vacio)')[:120])
        print('action:', resp.get('action'))
except urllib.error.HTTPError as e:
    print('Webhook HTTP error', e.code, e.read()[:300])
except Exception as ex:
    print('Webhook error:', ex)
