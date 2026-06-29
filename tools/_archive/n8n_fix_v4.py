import os
"""
Fix v4: Agrega tool buscar_cotizacion al AI Agent.
PATRÓN: igual que guardar_cotizacion y generar_pago:
  1. toolCode emite marker [BUSCAR_COT:numero=COT-XXXX-XXXXX]  (sin HTTP en sandbox)
  2. Nodo Code regular "Buscar en Supabase" intercepta el marker,
     hace la query HTTP real y devuelve la cotización formateada
Cadena: AI Agent → Guardar en Supabase → Buscar en Supabase → Generar Pago MP → Responder Webhook
"""
import urllib.request, json, uuid, time

API   = 'http://localhost:5678/api/v1'
KEY   = os.environ.get('N8N_API_KEY', '')
WF_ID = '4K4vFiRWRG63N92B'

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

# ─── Tool buscar_cotizacion (toolCode sandbox — solo emite marker) ────────────
TOOL_BUSCAR = r"""// toolCode sandbox: sin HTTP → solo emite marker para el nodo regular siguiente
let numero = '';
try {
  if (typeof query !== 'undefined' && query) {
    const q = (typeof query === 'string') ? query : JSON.stringify(query);
    const m = q.match(/COT-\d{4}-\d+/);
    numero = m ? m[0] : q.replace(/[^A-Z0-9-]/g, '').trim();
  }
} catch(e) { numero = ''; }

if (!numero || !numero.startsWith('COT-')) {
  return 'Necesito el número de cotización exacto (formato COT-2026-XXXXX) para buscarla.';
}

return '[BUSCAR_COT:numero=' + numero + ']';
"""

TOOL_BUSCAR_DESC = (
    'Busca una cotización existente en la base de datos por su número. '
    'Úsala SIEMPRE que el cliente mencione un número que empiece con COT- '
    'o pida ver, recuperar o pagar una cotización anterior. '
    'Pasa el número exacto (ej: COT-2026-93240). '
    'CRÍTICO: Copia literalmente el texto que devuelve la herramienta, sin agregar nada.'
)

# ─── Nodo Code regular "Buscar en Supabase" (this.helpers SÍ funciona aquí) ──
BUSCAR_NODE_CODE = r"""const agentOutput = $input.first().json;
const message = String(agentOutput.output || '');

// Solo actuar si hay marker de búsqueda
const buscarMatch = message.match(/\[BUSCAR_COT:numero=(COT-\d{4}-\d+)\]/);
if (!buscarMatch) {
  return [{ json: agentOutput }];
}

const numero = buscarMatch[1].trim();
const SUPABASE_URL = os.environ.get('SUPABASE_URL', '');
const SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '');
const fmt = n => Number(n || 0).toLocaleString('es-CL');

let newOutput;
try {
  const resp = await this.helpers.httpRequest({
    method: 'GET',
    url: SUPABASE_URL + '/rest/v1/cotizaciones?numero=eq.' + encodeURIComponent(numero) + '&limit=1',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY
    }
  });

  const data = Array.isArray(resp) ? resp : JSON.parse(String(resp));
  const row = data.length > 0 ? data[0] : null;

  if (!row) {
    newOutput = 'Esa cotización no existe. Si crees que el número es correcto, revísalo en el correo que recibiste cuando la generamos.';
  } else {
    const inst = row.instalacion ? 'Con instalación' : 'Sin instalación';
    const totalStr = row.total > 0 ? '$' + fmt(row.total) : 'A confirmar';
    newOutput = '✅ Cotización N° ' + row.numero + ' encontrada.\n'
              + '👤 ' + (row.nombre || '—') + ' — ' + (row.rut || '') + '\n'
              + '📍 ' + (row.direccion || '—') + '\n'
              + '🌿 ' + (row.producto || '—') + ' — ' + (row.m2 || 0) + ' m²\n'
              + '🔧 ' + inst + '\n'
              + '💰 Total: ' + totalStr + '\n\n'
              + 'Escribe PAGAR para continuar con el pago.';
  }
} catch(e) {
  newOutput = 'Error al buscar la cotización: ' + e.message;
}

return [{ json: { ...agentOutput, output: newOutput } }];
"""

# ─── Helpers ──────────────────────────────────────────────────────────────────
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
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print('PUT ERROR:', e.code, e.read().decode()[:500])
        raise

def api_post(path):
    req = urllib.request.Request(
        f'{API}/{path}', data=b'{}', method='POST',
        headers={'X-N8N-API-KEY': KEY, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def chat(msg, s):
    b = json.dumps({'message': msg, 'sessionId': s}).encode()
    req = urllib.request.Request(
        'http://localhost:5678/webhook/chat-v2', data=b, method='POST',
        headers={'Content-Type': 'application/json'}
    )
    return json.loads(urllib.request.urlopen(req, timeout=60).read()).get('message', '')

# ─── GET workflow ──────────────────────────────────────────────────────────────
wf = api_get(f'workflows/{WF_ID}')
print(f'Workflow: {wf["name"]} | {len(wf["nodes"])} nodos')

nodes = wf['nodes']
conns = wf['connections']

# Índice de nodos por nombre para fácil acceso
nmap = {n['name']: n for n in nodes}

# ─── 1. Tool buscar_cotizacion (toolCode — solo emite marker) ─────────────────
if 'Tool buscar_cotizacion' in nmap:
    n = nmap['Tool buscar_cotizacion']
    n['parameters']['jsCode'] = TOOL_BUSCAR
    n['parameters']['description'] = TOOL_BUSCAR_DESC
    print('✓ Tool buscar_cotizacion: actualizada')
else:
    last_pos = nmap.get('Tool generar_pago', {}).get('position', [512, 528])
    new_pos = [last_pos[0] + 160, last_pos[1]]
    nodes.append({
        'id': str(uuid.uuid4()),
        'name': 'Tool buscar_cotizacion',
        'type': '@n8n/n8n-nodes-langchain.toolCode',
        'typeVersion': 1.1,
        'position': new_pos,
        'parameters': {
            'name': 'buscar_cotizacion',
            'description': TOOL_BUSCAR_DESC,
            'jsCode': TOOL_BUSCAR
        }
    })
    print(f'✓ Tool buscar_cotizacion: nuevo nodo (pos {new_pos})')

# Conexión tool → AI Agent (ai_tool)
if 'Tool buscar_cotizacion' not in conns:
    conns['Tool buscar_cotizacion'] = {
        'ai_tool': [[{'node': 'AI Agent', 'type': 'ai_tool', 'index': 0}]]
    }
    print('✓ Conexión: Tool buscar_cotizacion → AI Agent')
else:
    print('  Conexión tool ya existe')

# ─── 2. Nodo Code regular "Buscar en Supabase" ────────────────────────────────
# Posición: entre Guardar en Supabase y Generar Pago MP
guardar_pos = nmap.get('Guardar en Supabase', {}).get('position', [0, 100])
generar_pos = nmap.get('Generar Pago MP', {}).get('position', [400, 100])
buscar_pos = [int((guardar_pos[0] + generar_pos[0]) / 2), guardar_pos[1]]

if 'Buscar en Supabase' in nmap:
    nmap['Buscar en Supabase']['parameters']['jsCode'] = BUSCAR_NODE_CODE
    print('✓ Nodo Buscar en Supabase: actualizado')
else:
    nodes.append({
        'id': str(uuid.uuid4()),
        'name': 'Buscar en Supabase',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': buscar_pos,
        'parameters': {
            'mode': 'runOnceForEachItem',
            'jsCode': BUSCAR_NODE_CODE
        }
    })
    print(f'✓ Nodo Buscar en Supabase: nuevo (pos {buscar_pos})')

# Reorganizar cadena principal:
# Guardar en Supabase → Buscar en Supabase → Generar Pago MP → Responder Webhook
# Primero: Guardar en Supabase → Buscar en Supabase
if 'Guardar en Supabase' in conns:
    # Averiguar a qué apuntaba antes (Generar Pago MP o Responder Webhook)
    main_targets = conns['Guardar en Supabase'].get('main', [[]])
    # Redirigir a Buscar en Supabase
    conns['Guardar en Supabase']['main'] = [[{'node': 'Buscar en Supabase', 'type': 'main', 'index': 0}]]
    print('✓ Conexión: Guardar en Supabase → Buscar en Supabase')

# Segundo: Buscar en Supabase → Generar Pago MP
conns['Buscar en Supabase'] = {
    'main': [[{'node': 'Generar Pago MP', 'type': 'main', 'index': 0}]]
}
print('✓ Conexión: Buscar en Supabase → Generar Pago MP')

# ─── 3. System prompt ─────────────────────────────────────────────────────────
REGLA_BUSCAR = (
    '\n== BÚSQUEDA DE COTIZACIONES ==\n'
    'Si el cliente menciona un número que empiece con COT- o pide ver/recuperar/pagar '
    'una cotización anterior: llama buscar_cotizacion pasando el número exacto (COT-XXXX-XXXXX). '
    'CRÍTICO: Copia literalmente el texto retornado por la herramienta, sin agregar nada.\n'
    'Si el cliente dice que NO recuerda o NO tiene su número de cotización '
    '(cualquier variante de "no recuerdo", "no sé", "no lo tengo", "no me acuerdo"), '
    'responde EXACTAMENTE: '
    '"Puedes encontrar tu número de cotización en el correo que te enviamos cuando la generamos. '
    'Búscalo con el asunto \'Cotización Césped Sintético ARM\'."'
)
for node in nodes:
    if node.get('type') == '@n8n/n8n-nodes-langchain.agent':
        prompt = node['parameters'].get('options', {}).get('systemMessage', '')
        if 'buscar_cotizacion' not in prompt:
            if '== REGLAS ESTRICTAS ==' in prompt:
                node['parameters']['options']['systemMessage'] = prompt.replace(
                    '== REGLAS ESTRICTAS ==',
                    REGLA_BUSCAR + '\n\n== REGLAS ESTRICTAS =='
                )
            else:
                node['parameters']['options']['systemMessage'] = prompt + '\n' + REGLA_BUSCAR
            print('✓ System prompt: regla buscar_cotizacion agregada')
        else:
            # Actualizar la regla existente
            import re
            new_prompt = re.sub(
                r'== BÚSQUEDA DE COTIZACIONES ==.*?(?=\n==|\Z)',
                REGLA_BUSCAR.strip(), prompt, flags=re.DOTALL
            )
            node['parameters']['options']['systemMessage'] = new_prompt
            print('✓ System prompt: regla buscar_cotizacion actualizada')

# ─── DEPLOY ───────────────────────────────────────────────────────────────────
wf['nodes'] = nodes
wf['connections'] = conns
result = api_put(WF_ID, wf)
print(f'\nPUT OK | nodes: {len(result["nodes"])} | active: {result.get("active")}')

if not result.get('active'):
    api_post(f'workflows/{WF_ID}/activate')
    print('Activated')

# ─── PRUEBA 1: Cotización existente ───────────────────────────────────────────
print('\n=== PRUEBA 1: Buscar COT-2026-93240 (existe en BD) ===')
time.sleep(3)
s1 = f'test-buscar-{int(time.time())}'
r1 = chat('Tengo el número COT-2026-93240, quiero ver mi cotización', s1)
print('R:', r1[:400])

# ─── PRUEBA 2: Número inexistente ─────────────────────────────────────────────
print('\n=== PRUEBA 2: COT-2026-00000 (no existe) ===')
time.sleep(2)
s2 = f'test-noexiste-{int(time.time())}'
r2 = chat('mi número es COT-2026-00000', s2)
print('R:', r2[:200])
