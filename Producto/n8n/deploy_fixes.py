"""
deploy_fixes.py
Deploy directo via API de n8n: actualiza solo los nodos corregidos.
  - "Construir Prompt Claude" -> nuevo codigo con instruccionInmediata
  - "Preparar Historial"      -> guarda rawText en vez de cleanText
"""
import urllib.request, urllib.error, json, sys, time
from pathlib import Path

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'
WF_ID   = 'CjS3Gm0863S4j9Ij'
BASE    = 'http://localhost:5678/api/v1'

# Codigo nuevo para "Construir Prompt Claude" (desde construir_code.txt)
CODE_FILE = Path(__file__).parent / 'construir_code.txt'
NEW_CONSTRUIR = CODE_FILE.read_text(encoding='utf-8')

# Codigo nuevo para "Preparar Historial" (guarda rawText)
NEW_PREPARAR = (
    "const extract = $('Extraer Input').first()?.json || {};\n"
    "const parse   = $('Parsear Respuesta Claude').first()?.json || {};\n"
    "\n"
    "const uuid         = extract.uuid || 'anonimo';\n"
    "const userMsg      = extract.message || '';\n"
    "// rawText mantiene etiquetas [COTIZAR:] para que el estado no se rompa\n"
    "const assistantMsg = parse.rawText || parse.cleanText || parse.fullResponse || '';\n"
    "\n"
    "let history = [];\n"
    "try {\n"
    "  const raw = $('GET Historial Supabase').first()?.json;\n"
    "  if (Array.isArray(raw) && raw.length > 0 && Array.isArray(raw[0].messages)) {\n"
    "    history = raw[0].messages;\n"
    "  } else if (raw && Array.isArray(raw.messages)) {\n"
    "    history = raw.messages;\n"
    "  }\n"
    "} catch(e) {}\n"
    "\n"
    "if (!Array.isArray(history) || history.length === 0) {\n"
    "  try {\n"
    "    const bh = extract.bodyHistory;\n"
    "    if (Array.isArray(bh)) history = bh;\n"
    "  } catch(e) {}\n"
    "}\n"
    "\n"
    "if (!Array.isArray(history)) history = [];\n"
    "history = history.filter(m => m && m.content);\n"
    "\n"
    "history.push({ role: 'user',      content: userMsg      });\n"
    "history.push({ role: 'assistant', content: assistantMsg });\n"
    "history = history.slice(-40);\n"
    "\n"
    "return [{ json: { uuid, history, message: userMsg, assistantMsg } }];"
)

# ── Utilidades API ─────────────────────────────────────────────────────────────
def n8n_request(path, method='GET', data=None):
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header('X-N8N-API-KEY', API_KEY)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f'  HTTP {e.code}: {e.read().decode()[:400]}')
        return None
    except Exception as ex:
        print(f'  Error: {ex}')
        return None

# ── Deploy ─────────────────────────────────────────────────────────────────────
print('1. Obteniendo workflow actual...')
wf = n8n_request(f'/workflows/{WF_ID}')
if not wf:
    print('   No se pudo obtener el workflow. Verifica que n8n este corriendo.')
    sys.exit(1)
print(f'   Workflow: "{wf.get("name")}" ({len(wf["nodes"])} nodos)')

print('2. Aplicando cambios a los nodos...')
patched = {'construir': False, 'preparar': False}
for node in wf['nodes']:
    name   = node.get('name', '')
    params = node.get('parameters', {})
    if name == 'Construir Prompt Claude' and 'jsCode' in params:
        params['jsCode'] = NEW_CONSTRUIR
        patched['construir'] = True
        print('   [OK] "Construir Prompt Claude" actualizado')
    elif name == 'Preparar Historial' and 'jsCode' in params:
        params['jsCode'] = NEW_PREPARAR
        patched['preparar'] = True
        print('   [OK] "Preparar Historial" actualizado')

if not patched['construir']:
    print('   [WARN] Nodo "Construir Prompt Claude" no encontrado')
if not patched['preparar']:
    print('   [WARN] Nodo "Preparar Historial" no encontrado')

print('3. Desactivando workflow...')
n8n_request(f'/workflows/{WF_ID}/deactivate', 'POST', b'{}')

print('4. Guardando cambios via PUT...')
raw_settings = wf.get('settings', {})
clean_settings = {}
for k in ('executionOrder', 'saveManualExecutions', 'callerPolicy',
          'errorWorkflow', 'timezone', 'saveDataErrorExecution',
          'saveDataSuccessExecution', 'saveExecutionProgress'):
    if k in raw_settings:
        clean_settings[k] = raw_settings[k]

payload = json.dumps({
    'name':        wf['name'],
    'nodes':       wf['nodes'],
    'connections': wf['connections'],
    'settings':    clean_settings,
}).encode('utf-8')

result = n8n_request(f'/workflows/{WF_ID}', 'PUT', payload)
if not result:
    print('   ERROR: no se pudo guardar. Abortando.')
    sys.exit(1)
print(f'   Guardado. Nodos: {len(result["nodes"])}')

print('5. Reactivando...')
time.sleep(1)
n8n_request(f'/workflows/{WF_ID}/activate', 'POST', b'{}')
print('   Activo.')

print('6. Probando con mensaje de prueba...')
time.sleep(2)
test_body = json.dumps({
    'message':   'hola, quiero informacion sobre el pasto',
    'sessionId': 'test-deploy-fix-v2',
    'history':   []
}).encode('utf-8')
req = urllib.request.Request(
    'http://localhost:5678/webhook/chat', data=test_body, method='POST')
req.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req, timeout=35) as r:
        resp = json.loads(r.read())
        msg = resp.get('message', '(sin respuesta)')
        print(f'   Respuesta: {msg[:150]}')
        print(f'   Accion:    {resp.get("action", "CHAT")}')
        print('\nDeploy exitoso.')
except urllib.error.HTTPError as e:
    print(f'   HTTP {e.code}: {e.read()[:200].decode()}')
except Exception as ex:
    print(f'   Error en test: {ex}')
