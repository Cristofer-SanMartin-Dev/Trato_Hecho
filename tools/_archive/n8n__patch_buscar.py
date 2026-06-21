import os
import urllib.request, json, re

API = 'http://localhost:5678/api/v1'
KEY = os.environ.get('N8N_API_KEY', '')
WF_ID = '4K4vFiRWRG63N92B'

def api_get(path):
    req = urllib.request.Request(f'{API}/{path}', headers={'X-N8N-API-KEY': KEY})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def api_put(wf_id, wf):
    ALLOWED = {'executionOrder','callerPolicy','saveDataSuccessExecution',
               'saveDataErrorExecution','saveManualExecutions','timezone',
               'errorWorkflow','saveExecutionProgress'}
    body = {
        'name': wf['name'], 'nodes': wf['nodes'],
        'connections': wf['connections'],
        'settings': {k:v for k,v in wf.get('settings',{}).items() if k in ALLOWED},
        'staticData': wf.get('staticData', None),
    }
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f'{API}/workflows/{wf_id}', data=data, method='PUT',
        headers={'X-N8N-API-KEY': KEY, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

wf = api_get(f'workflows/{WF_ID}')
nodes = wf['nodes']

# ── 1. Actualizar nodo "Buscar en Supabase" ───────────────────────────────────
VIEJO = "newOutput = 'No encontré la cotización ' + numero + '. Verifica el número e intenta de nuevo.';"
NUEVO  = "newOutput = 'Esa cotización no existe. Si crees que el número es correcto, revísalo en el correo que recibiste cuando la generamos.';"

for node in nodes:
    if node['name'] == 'Buscar en Supabase':
        code = node['parameters']['jsCode']
        if VIEJO in code:
            node['parameters']['jsCode'] = code.replace(VIEJO, NUEVO)
            print('✓ Buscar en Supabase: mensaje actualizado')
        elif 'Esa cotización no existe' in code:
            print('  Buscar en Supabase: ya estaba actualizado')
        else:
            print('  AVISO: patrón no encontrado en el nodo')

# ── 2. Actualizar system prompt del AI Agent ──────────────────────────────────
NUEVA_SECCION = (
    '== BÚSQUEDA DE COTIZACIONES ==\n'
    '- SOLO llama buscar_cotizacion cuando el cliente mencione un número COT-XXXX-XXXXX explícito.\n'
    '- Cuando el cliente proporcione un número COT: llama ÚNICAMENTE buscar_cotizacion. '
    'NO llames guardar_cotizacion. NO generes una cotización nueva.\n'
    '- Copia literalmente el texto que devuelve buscar_cotizacion como tu respuesta. No agregues nada.\n'
    '- Si el cliente quiere buscar una cotización, NUNCA llames guardar_cotizacion.\n'
    '- Si el cliente dice que NO recuerda o NO tiene su número de cotización '
    '(cualquier variante de "no recuerdo", "no sé", "no lo tengo", "no me acuerdo"), '
    'responde EXACTAMENTE: '
    '"Puedes encontrar tu número de cotización en el correo que te enviamos cuando la generamos. '
    "Búscalo con el asunto 'Cotización Césped Sintético ARM'.\""
)

for node in nodes:
    if node.get('type') == '@n8n/n8n-nodes-langchain.agent':
        prompt = node['parameters'].get('options', {}).get('systemMessage', '')
        new_prompt = re.sub(
            r'== BÚSQUEDA DE COTIZACIONES ==.*?(?=\n==|\Z)',
            NUEVA_SECCION,
            prompt,
            flags=re.DOTALL
        )
        if new_prompt != prompt:
            node['parameters']['options']['systemMessage'] = new_prompt
            print('✓ System prompt: sección BÚSQUEDA DE COTIZACIONES actualizada')
        else:
            print('  System prompt: sin cambios detectados')

# ── 3. Deploy ─────────────────────────────────────────────────────────────────
wf['nodes'] = nodes
result = api_put(WF_ID, wf)
print(f'\nPUT OK | nodes: {len(result["nodes"])} | active: {result.get("active")}')
