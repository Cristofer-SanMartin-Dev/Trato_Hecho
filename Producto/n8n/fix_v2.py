"""
Fix v2: Solución correcta para guardar en Supabase.
- toolCode sandbox NO tiene fetch/https/http/axios/$helpers
- Solución: tool solo genera COT y retorna string formateado
- Nuevo nodo Code regular "Guardar en Supabase" (donde this.helpers.httpRequest SÍ funciona)
- Conexiones: AI Agent → Guardar en Supabase → Responder Webhook
"""
import urllib.request, json, time, uuid

API = 'http://localhost:5678/api/v1'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'
WF_ID = '4K4vFiRWRG63N92B'

SUPABASE_URL = 'https://enpzxntzphvezopbxbtx.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVucHp4bnR6cGh2ZXpvcGJ4YnR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc3MTEzMDUsImV4cCI6MjA5MzI4NzMwNX0.kdT61HJFXFiDXPQUqwZivOmjDFJO3aoY7XETf_LoZQ4'

# ─── TOOL CODE (sin HTTP — solo genera COT y retorna string) ──────────────────
# El sandbox toolCode NO tiene fetch / https / $helpers
# La persistencia en Supabase la hace el nodo Code regular que viene después
TOOL_GUARDAR_SIMPLE = r"""// En toolCode, el LLM pasa los datos como variable 'query' (string JSON)
let inp = {};
try {
  if (typeof query !== 'undefined' && query) {
    inp = (typeof query === 'string') ? JSON.parse(query) : query;
  } else {
    const raw = $input.first().json;
    const q = raw.query || raw;
    inp = (typeof q === 'string') ? JSON.parse(q) : q;
  }
} catch(e) { inp = {}; }

const year = new Date().getFullYear();
const seq = String(Date.now()).slice(-5);
const numero = 'COT-' + year + '-' + seq;

const m2 = Math.round(parseFloat(String(inp.m2 || inp.metros_cuadrados || '0').replace(/[^0-9.]/g, '')) || 0);
const rawTotal = String(inp.total || '0').replace(/[^0-9]/g, '');
const total = parseInt(rawTotal) || 0;

const nombre = String(inp.nombre || '');
const rut = String(inp.rut || '');
const direccion = String(inp.direccion || '');
const producto = String(inp.producto || '');

const fmt = n => Number(n).toLocaleString('es-CL');
const totalStr = total > 0 ? '$' + fmt(total) : 'A cotizar';
const footerStr = total > 0
  ? 'Escribe PAGAR para continuar con el pago.'
  : 'Un asesor te contactar\u00e1 con el precio final.';

return '\u2705 Cotizaci\u00f3n N\u00b0 ' + numero + ' generada.\n\ud83d\udc64 ' + nombre + ' \u2014 ' + rut + '\n\ud83d\udccd ' + direccion + '\n\ud83c\udf3f ' + producto + ' \u2014 ' + m2 + ' m\u00b2\n\ud83d\udcb0 Total: ' + totalStr + '\n\n' + footerStr;
"""

# ─── NODO CODE: Guardar en Supabase (nodo regular donde helpers SÍ funciona) ─
SUPABASE_NODE_CODE = r"""
const agentOutput = $input.first().json;
const message = String(agentOutput.output || '');

// Solo procesar si el mensaje contiene un número de cotización
const cotMatch = message.match(/COT-(\d{4}-\d+)/);
if (!cotMatch) {
  return [{ json: agentOutput }];
}

const numero = 'COT-' + cotMatch[1];
let nombre = '', rut = '', direccion = '', producto = '', m2 = 0, total = 0;

const lines = message.split('\n');
for (const line of lines) {
  const l = line.trim();
  if (l.includes('\ud83d\udc64')) {
    const parts = l.replace(/^.*\ud83d\udc64\s*/, '').split(' \u2014 ');
    nombre = (parts[0] || '').trim();
    rut = (parts[1] || '').trim();
  } else if (l.includes('\ud83d\udccd')) {
    direccion = l.replace(/^.*\ud83d\udccd\s*/, '').trim();
  } else if (l.includes('\ud83c\udf3f')) {
    const parts = l.replace(/^.*\ud83c\udf3f\s*/, '').split(' \u2014 ');
    producto = (parts[0] || '').trim();
    m2 = parseInt((parts[1] || '').replace(/[^0-9]/g, '')) || 0;
  } else if (l.includes('\ud83d\udcb0')) {
    // Puede ser "$825.000" o "A cotizar"
    const afterDollar = l.indexOf('$');
    if (afterDollar !== -1) {
      total = parseInt(l.slice(afterDollar + 1).replace(/[^0-9]/g, '')) || 0;
    } else {
      total = 0; // A cotizar / deportivo
    }
  }
}

let sessionId = '';
try { sessionId = $('Extraer Input').first().json.sessionId || ''; } catch(e) {}

const SUPABASE_URL = 'https://enpzxntzphvezopbxbtx.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVucHp4bnR6cGh2ZXpvcGJ4YnR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc3MTEzMDUsImV4cCI6MjA5MzI4NzMwNX0.kdT61HJFXFiDXPQUqwZivOmjDFJO3aoY7XETf_LoZQ4';

const quote = {
  numero,
  session_id: sessionId,
  nombre, rut, direccion, producto,
  m2, instalacion: true, total,
  estado: 'pendiente'
};

try {
  await this.helpers.httpRequest({
    method: 'POST',
    url: SUPABASE_URL + '/rest/v1/cotizaciones',
    headers: {
      'Content-Type': 'application/json',
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Prefer': 'return=minimal'
    },
    body: JSON.stringify(quote)
  });
} catch(e) {
  // No fallar el flujo por error de Supabase
  console.error('Supabase error:', e.message);
}

return [{ json: agentOutput }];
"""

# ─── TOOL CODE: calcular_precio (con precios para todos los productos) ────────
TOOL_CALCULAR_FIXED = r"""const inp = $input.first().json;
const producto = String(inp.producto || '').toLowerCase();
const m2 = parseFloat(inp.m2) || 0;
const conInst = inp.con_instalacion === true || inp.con_instalacion === 'true' || inp.con_instalacion === 'SI';

const PRECIOS = {
  // Residenciales
  'luxury': 28500,
  'emerald': 28500,
  'soft touch': 22900,
  'soft': 22900,
  'pet': 26000,
  'friendly': 26000,
  // Deportivos (precios provisionales)
  'futbol 7': 35000,
  'fútbol 7': 35000,
  'futbol7': 35000,
  'fútbol7': 35000,
  'futbol 11': 32000,
  'fútbol 11': 32000,
  'futbol11': 32000,
  'fútbol11': 32000,
  'tenis': 38000,
  'padel': 38000,
  'pádel': 38000,
  'deportivo': 34000,
};

let precioPorM2 = 0;
for (const [key, price] of Object.entries(PRECIOS)) {
  if (producto.includes(key)) { precioPorM2 = price; break; }
}

if (m2 <= 0) {
  return [{ json: { error: 'Se necesitan los m² para calcular' } }];
}
if (precioPorM2 === 0) {
  return [{ json: { error: 'Producto no reconocido: ' + inp.producto } }];
}

const m2Margen = Math.ceil(m2 * 1.10);
const subtotalPasto = m2Margen * precioPorM2;
const subtotalInst = conInst ? m2Margen * 4500 : 0;
const total = subtotalPasto + subtotalInst;

const fmt = n => n.toLocaleString('es-CL');

return [{
  json: {
    producto: inp.producto,
    m2_original: m2,
    m2_con_margen: m2Margen,
    precio_por_m2: precioPorM2,
    subtotal_pasto: subtotalPasto,
    instalacion: conInst,
    subtotal_instalacion: subtotalInst,
    total,
    resumen: `${inp.producto} — $${fmt(precioPorM2)}/m²\nSuperficie: ${m2} m² → ${m2Margen} m² (con margen técnico 10%)\nSubtotal pasto: $${fmt(subtotalPasto)}${conInst ? `\nInstalación: $${fmt(subtotalInst)}` : '\nInstalación: no incluida'}\nTOTAL: $${fmt(total)}`
  }
}];"""

# ─── SYSTEM PROMPT ────────────────────────────────────────────────────────────
NEW_SYSTEM_PROMPT = """Eres Queno, asesor virtual de Césped Sintético ARM en Melipilla, Chile.
Vendes césped sintético, calculas precios exactos con tus herramientas y generas cotizaciones formales.

== CATÁLOGO (precios CLP/m², con IVA) ==
- Luxury Emerald 40mm: $28.500/m² — jardín o terraza premium
- Soft Touch 30mm: $22.900/m² — jardín residencial, suave al tacto
- Pet-Friendly Turf 35mm: $26.000/m² — jardines con mascotas, fibra antimicrobiana
- Pasto Deportivo Fútbol 7: $35.000/m²
- Pasto Deportivo Fútbol 11: $32.000/m²
- Pasto Tenis & Pádel: $38.000/m²
- Instalación opcional: +$4.500/m² (solo productos residenciales)

== FLUJO DE VENTA ==
1. Pregunta si necesita jardín/terraza o cancha deportiva
2. Muestra las opciones según el tipo elegido
3. Cliente elige producto → pregunta: "¿Conoces las medidas de tu espacio (largo y ancho)?"
   - Si RESPONDE CON MEDIDAS o SÍ sabe → pide los m² o interpreta las dimensiones directamente
   - Si dice NO sabe / no tiene las medidas → muestra calculadora (ver sección CALCULADORA)
4. Con producto + m² definidos → llama calcular_precio (incluye con_instalacion si ya lo sabe)
5. Muestra el desglose y pregunta: "¿Necesita instalación? (+$4.500/m²) — responde SI o NO"
6. Con instalación definida → muestra total y di: "Escribe COTIZAR para tu cotización formal"
7. Producto deportivo + m² → llama calcular_precio, muestra resumen y di: "Escribe COTIZAR para tu cotización formal"
8. Cliente escribe COTIZAR → pide nombre completo
9. Nombre obtenido → pide RUT (formato: 12.345.678-9)
10. RUT obtenido → pide dirección completa de instalación
11. Dirección obtenida → llama guardar_cotizacion con todos los datos. La herramienta devuelve una cadena de texto. DEBES RESPONDER AL USUARIO CON ESA CADENA EXACTAMENTE, sin agregar ninguna palabra, sin saludos, sin reformatear, sin resumir. Tu respuesta debe ser única y exclusivamente el texto devuelto por la herramienta.

== INTERPRETACIÓN DE MEDIDAS ==
- Número solo (40) o con unidad (40m2, 40 metros) = metros cuadrados directos
- Dos números (5x8, 5 por 8, 5*8) = largo × ancho → multiplica para obtener m²
- EXCEPCIÓN: cuando estés pidiendo nombre, RUT o dirección, NO interpretes texto como m²

== CALCULADORA DE METRAJE ==
Cuando el cliente diga que NO sabe sus metros cuadrados (cualquier variante de "no sé", "no tengo idea", "no las tengo", "no sé las medidas", "no lo se", "no se", "no sé cuántos", "no tengo las medidas", "no conozco"), responde EXACTAMENTE así, sin cambiar nada, sin agregar texto antes ni después:
"No hay problema, te muestro la calculadora. Ingresa el largo y ancho de tu terreno: [CALC]"

El marcador [CALC] DEBE estar al final de la frase. NUNCA describas la calculadora con texto adicional. NUNCA digas "la calculadora aparece arriba" ni nada similar. Solo responde esa frase exacta con [CALC] al final.

== REGLAS ESTRICTAS ==
- Máximo 4 líneas por respuesta. Solo 1 pregunta por mensaje.
- NUNCA saludar con "Hola" si ya hay historial anterior.
- NUNCA volver a preguntar algo que el cliente ya respondió.
- Si el cliente escribe PAGAR y ya hay cotización: llama generar_pago con el número de cotización."""

TOOL_GUARDAR_DESC = (
    'Guarda la cotización en la base de datos. '
    'Úsala cuando tengas nombre, RUT, dirección, producto, m² y total. '
    'CRÍTICO: La herramienta retorna una cadena de texto. '
    'Esa cadena ES TU RESPUESTA COMPLETA al usuario — cópiala literalmente sin cambiar nada.'
)

# ─── TOOL CODE: generar_pago (sin HTTP — igual que guardar_cotizacion) ────────
# fetch NO está disponible en toolCode sandbox → solo retorna string con info de pago
TOOL_PAGO_FIXED = r"""// En toolCode el LLM pasa datos como variable 'query' (string JSON)
let inp = {};
try {
  if (typeof query !== 'undefined' && query) {
    inp = (typeof query === 'string') ? JSON.parse(query) : query;
  } else {
    const raw = $input.first().json;
    const q = raw.query || raw;
    inp = (typeof q === 'string') ? JSON.parse(q) : q;
  }
} catch(e) { inp = {}; }

const numero = String(inp.numero_cotizacion || inp.numero || '');
const total = parseInt(String(inp.total || '0').replace(/[^0-9]/g, '')) || 0;
const fmt = n => Number(n).toLocaleString('es-CL');
const totalStr = total > 0 ? '$' + fmt(total) : 'A confirmar';

return '\ud83d\udcb3 Pago para ' + numero + '\n\ud83d\udcb0 Total: ' + totalStr + '\n\nUn asesor te enviará el link de pago a la brevedad.\nTambién puedes contactarnos al +56 9 XXXX XXXX.';
"""

TOOL_PAGO_DESC = (
    'Genera el proceso de pago para una cotización existente. '
    'Llámala cuando el cliente escriba PAGAR. '
    'Pasa numero_cotizacion (el número COT-XXXX-XXXXX) y total (el monto en números). '
    'CRÍTICO: La herramienta retorna una cadena de texto. '
    'Esa cadena ES TU RESPUESTA COMPLETA al usuario — cópiala literalmente sin cambiar nada.'
)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def api_get(path):
    req = urllib.request.Request(f'{API}/{path}', headers={'X-N8N-API-KEY': KEY})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def api_put(wf_id, wf):
    # Only include settings properties accepted by n8n PUT API
    ALLOWED_SETTINGS = {'executionOrder', 'callerPolicy', 'saveDataSuccessExecution',
                        'saveDataErrorExecution', 'saveManualExecutions', 'timezone',
                        'errorWorkflow', 'saveExecutionProgress'}
    raw_settings = wf.get('settings', {})
    settings = {k: v for k, v in raw_settings.items() if k in ALLOWED_SETTINGS}
    body = {
        'name': wf['name'],
        'nodes': wf['nodes'],
        'connections': wf['connections'],
        'settings': settings,
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
        body_err = e.read().decode()
        print('PUT ERROR:', e.code, body_err[:500])
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
    req = urllib.request.Request('http://localhost:5678/webhook/chat-v2', data=b, method='POST',
                                  headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read()).get('message', '')

# ─── GET WORKFLOW ──────────────────────────────────────────────────────────────
wf = api_get(f'workflows/{WF_ID}')
print('Got workflow:', wf['name'], '| active:', wf.get('active'))

# ─── PATCH NODES ──────────────────────────────────────────────────────────────
SUPABASE_NODE_ID = str(uuid.uuid4())
supabase_node_exists = any(n['name'] == 'Guardar en Supabase' for n in wf['nodes'])

for node in wf['nodes']:
    # Fix Anthropic LLM
    if node.get('type') == '@n8n/n8n-nodes-langchain.lmChatAnthropic':
        node['typeVersion'] = 1.3
        node['parameters']['model'] = {'__rl': True, 'value': 'claude-sonnet-4-5', 'mode': 'id'}
        node['parameters'].setdefault('options', {})['maxTokens'] = 1024
        print('✓ LLM: typeVersion=1.3, model=claude-sonnet-4-5')

    # Fix system prompt
    if node.get('type') == '@n8n/n8n-nodes-langchain.agent':
        node['parameters'].setdefault('options', {})['systemMessage'] = NEW_SYSTEM_PROMPT
        print('✓ Agent: system prompt updated')

    # Fix calcular_precio tool (add sports product prices)
    if node.get('name') == 'Tool calcular_precio':
        node['parameters']['jsCode'] = TOOL_CALCULAR_FIXED
        print('✓ Tool calcular_precio: sports prices added')

    # Fix guardar_cotizacion tool (simple, no HTTP)
    if node.get('name') == 'Tool guardar_cotizacion':
        node['parameters']['jsCode'] = TOOL_GUARDAR_SIMPLE
        node['parameters']['description'] = TOOL_GUARDAR_DESC
        print('✓ Tool guardar_cotizacion: simplified (no HTTP in sandbox)')

    # Fix generar_pago tool (fetch not available in toolCode sandbox)
    if node.get('name') == 'Tool generar_pago':
        node['parameters']['jsCode'] = TOOL_PAGO_FIXED
        node['parameters']['description'] = TOOL_PAGO_DESC
        print('✓ Tool generar_pago: fixed (no fetch in sandbox)')

    # Update existing Supabase node if it exists
    if node.get('name') == 'Guardar en Supabase':
        node['parameters']['jsCode'] = SUPABASE_NODE_CODE
        SUPABASE_NODE_ID = node['id']
        print('✓ Guardar en Supabase: code updated (existing node)')

# Add new Supabase node if it doesn't exist
if not supabase_node_exists:
    new_node = {
        'id': SUPABASE_NODE_ID,
        'name': 'Guardar en Supabase',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [215, 300],
        'parameters': {
            'jsCode': SUPABASE_NODE_CODE,
            'mode': 'runOnceForAllItems'
        }
    }
    wf['nodes'].append(new_node)
    print('✓ Guardar en Supabase: new node added')

# ─── UPDATE CONNECTIONS ────────────────────────────────────────────────────────
# Goal: AI Agent → Guardar en Supabase → Responder Webhook
# Remove direct: AI Agent → Responder Webhook
# Add: AI Agent → Guardar en Supabase
# Add: Guardar en Supabase → Responder Webhook

conns = wf['connections']

# Find what AI Agent currently connects to on main[0]
ai_main = conns.get('AI Agent', {}).get('main', [[]])[0]
# Remove direct connection to Responder Webhook if present
ai_main_filtered = [c for c in ai_main if c.get('node') != 'Responder Webhook']
# Add connection to Guardar en Supabase if not already there
if not any(c.get('node') == 'Guardar en Supabase' for c in ai_main_filtered):
    ai_main_filtered.append({'node': 'Guardar en Supabase', 'type': 'main', 'index': 0})
conns.setdefault('AI Agent', {})['main'] = [ai_main_filtered]

# Add Guardar en Supabase → Responder Webhook
conns['Guardar en Supabase'] = {
    'main': [[{'node': 'Responder Webhook', 'type': 'main', 'index': 0}]]
}

print('✓ Connections: AI Agent → Guardar en Supabase → Responder Webhook')

# ─── DEPLOY ───────────────────────────────────────────────────────────────────
result = api_put(WF_ID, wf)
print(f'\nPUT OK | nodes: {len(result["nodes"])} | active: {result.get("active")}')

if not result.get('active'):
    api_post(f'workflows/{WF_ID}/activate')
    print('Activated')

# ─── TEST ─────────────────────────────────────────────────────────────────────
print('\n--- Prueba completa ---')
time.sleep(2)
s = f'test-v2-{int(time.time())}'

r1 = chat('hola, necesito césped para jardín, tengo 25m2, luxury emerald con instalacion', s)
print('T1:', r1[:120])
time.sleep(1)

r2 = chat('COTIZAR', s)
print('T2:', r2[:120])
time.sleep(1)

r3 = chat('Pedro Soto', s)
print('T3:', r3[:120])
time.sleep(1)

r4 = chat('9.876.543-2', s)
print('T4:', r4[:120])
time.sleep(1)

r5 = chat('Calle Los Pinos 789, Melipilla', s)
print('T5 (COT):', r5[:200])

# ─── VERIFICAR SUPABASE ───────────────────────────────────────────────────────
print('\n--- Verificando Supabase ---')
time.sleep(3)
sb_req = urllib.request.Request(
    f'{SUPABASE_URL}/rest/v1/cotizaciones?order=created_at.desc&limit=3',
    headers={'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}
)
rows = json.loads(urllib.request.urlopen(sb_req).read())
print(f'Supabase rows: {len(rows)}')
for row in rows:
    print(' -', row.get('numero'), row.get('nombre'), row.get('total'))
