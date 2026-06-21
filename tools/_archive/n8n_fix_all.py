import os
"""
Fix combinado:
1. Anthropic LLM node -> typeVersion 1.3 + claude-sonnet-4-5 resource locator
2. Sistema prompt -> paso 10 con instrucción de copiar verbatim
3. Tool guardar_cotizacion -> Math.round(m2) para integer column + error detallado
"""
import urllib.request, json, time

# ─── TOOL: guardar_cotizacion (fixed) ────────────────────────────────────────
# toolCode nodes: must return string; fetch not available → use $helpers.httpRequest
TOOL_GUARDAR_FIXED = r"""const inp = $input.first().json;
const SUPABASE_URL = os.environ.get('SUPABASE_URL', '');
const SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '');

const year = new Date().getFullYear();
const seq = String(Date.now()).slice(-5);
const numero = 'COT-' + year + '-' + seq;

// m2 MUST be integer for Supabase schema
const m2 = Math.round(parseFloat(String(inp.m2 || inp.metros_cuadrados || '0').replace(/[^0-9.]/g, '')) || 0);

// total: strip all non-digit characters
const rawTotal = String(inp.total || '0').replace(/[^0-9]/g, '');
const total = parseInt(rawTotal) || 0;

const nombre = String(inp.nombre || '');
const rut = String(inp.rut || '');
const direccion = String(inp.direccion || '');
const producto = String(inp.producto || '');
const instalacion = inp.instalacion === true || inp.con_instalacion === true ||
  String(inp.instalacion || inp.con_instalacion || '').toUpperCase() === 'SI' ||
  String(inp.instalacion || inp.con_instalacion || '') === 'true';

const quote = {
  numero,
  session_id: String(inp.session_id || ''),
  nombre, rut, direccion, producto, m2, instalacion, total,
  estado: 'pendiente'
};

try {
  const resp = await $helpers.httpRequest({
    method: 'POST',
    url: SUPABASE_URL + '/rest/v1/cotizaciones',
    headers: {
      'Content-Type': 'application/json',
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Prefer': 'return=minimal'
    },
    body: JSON.stringify(quote),
    returnFullResponse: true,
    ignoreHttpStatusErrors: true
  });

  const ok = resp.statusCode >= 200 && resp.statusCode < 300;
  const fmt = n => Number(n).toLocaleString('es-CL');

  if (ok) {
    return '\u2705 Cotizaci\u00f3n N\u00b0 ' + numero + ' generada.\n\ud83d\udc64 ' + nombre + ' \u2014 ' + rut + '\n\ud83d\udccd ' + direccion + '\n\ud83c\udf3f ' + producto + ' \u2014 ' + m2 + ' m\u00b2\n\ud83d\udcb0 Total: $' + fmt(total) + '\n\nEscribe PAGAR para continuar con el pago.';
  } else {
    return 'Error guardando cotizacion: HTTP ' + resp.statusCode + ' ' + JSON.stringify(resp.body).slice(0, 200);
  }
} catch(e) {
  return 'Error: ' + String(e.message);
}"""

API = 'http://localhost:5678/api/v1'
KEY = os.environ.get('N8N_API_KEY', '')
WF_ID = '4K4vFiRWRG63N92B'

NEW_SYSTEM_PROMPT = """Eres Queno, asesor virtual de Césped Sintético ARM en Melipilla, Chile.
Vendes césped sintético, calculas precios exactos con tus herramientas y generas cotizaciones formales.

== CATÁLOGO (precios CLP/m², con IVA) ==
- Luxury Emerald 40mm: $28.500/m² — jardín o terraza premium
- Soft Touch 30mm: $22.900/m² — jardín residencial, suave al tacto
- Pet-Friendly Turf 35mm: $26.000/m² — jardines con mascotas, fibra antimicrobiana
- Pasto Deportivo Fútbol 7: precio a cotizar
- Pasto Deportivo Fútbol 11: precio a cotizar
- Pasto Tenis & Pádel: precio a cotizar
- Instalación opcional: +$4.500/m² (solo productos residenciales)

== FLUJO DE VENTA ==
1. Pregunta si necesita jardín/terraza o cancha deportiva
2. Muestra las opciones según el tipo elegido
3. Con producto + m² definidos → llama calcular_precio (incluye con_instalacion si ya lo sabe)
4. Muestra el desglose y pregunta: "¿Necesita instalación? (+$4.500/m²) — responde SI o NO"
5. Con instalación definida → muestra total y di: "Escribe COTIZAR para tu cotización formal"
6. Producto deportivo + m² → muestra resumen y di: "Escribe COTIZAR para cotización formal"
7. Cliente escribe COTIZAR → pide nombre completo
8. Nombre obtenido → pide RUT (formato: 12.345.678-9)
9. RUT obtenido → pide dirección completa de instalación
10. Dirección obtenida → llama guardar_cotizacion con todos los datos → tu respuesta al usuario debe ser EXACTAMENTE el campo "mensaje" del resultado, sin cambiar ni una sola letra, sin agregar texto, sin reformatear, sin resumir. Copia y pega el campo "mensaje" tal cual.

== INTERPRETACIÓN DE MEDIDAS ==
- Número solo (40) o con unidad (40m2, 40 metros) = metros cuadrados directos
- Dos números (5x8, 5 por 8, 5*8) = largo × ancho → multiplica para obtener m²
- EXCEPCIÓN: cuando estés pidiendo nombre, RUT o dirección, NO interpretes texto como m²

== REGLAS ESTRICTAS ==
- Máximo 4 líneas por respuesta. Solo 1 pregunta por mensaje.
- NUNCA saludar con "Hola" si ya hay historial anterior.
- NUNCA volver a preguntar algo que el cliente ya respondió.
- NUNCA calcular precios para productos deportivos — son "precio a cotizar".
- Si el cliente no sabe sus medidas: explica brevemente cómo medir (largo × ancho).
- Si el cliente escribe PAGAR y ya hay cotización: llama generar_pago con el número de cotización."""

def api_get(path):
    req = urllib.request.Request(f'{API}/{path}', headers={'X-N8N-API-KEY': KEY})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def api_put(wf_id, wf):
    body = {
        'name': wf['name'],
        'nodes': wf['nodes'],
        'connections': wf['connections'],
        'settings': wf.get('settings', {}),
        'staticData': wf.get('staticData', None),
    }
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f'{API}/workflows/{wf_id}',
        data=data, method='PUT',
        headers={'X-N8N-API-KEY': KEY, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def api_post(path):
    req = urllib.request.Request(
        f'{API}/{path}', data=b'{}', method='POST',
        headers={'X-N8N-API-KEY': KEY, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# ─── GET WORKFLOW ────────────────────────────────────────────────────────────
wf = api_get(f'workflows/{WF_ID}')
print('Got workflow:', wf['name'], '| active:', wf.get('active'))

fixed_llm = False
fixed_prompt = False
fixed_tool_desc = False
fixed_tool_code = False

for node in wf['nodes']:
    # 1. Fix Anthropic LLM node
    if node.get('type') == '@n8n/n8n-nodes-langchain.lmChatAnthropic':
        old = node.get('typeVersion'), node['parameters'].get('model')
        node['typeVersion'] = 1.3
        node['parameters']['model'] = {'__rl': True, 'value': 'claude-sonnet-4-5', 'mode': 'id'}
        node['parameters'].setdefault('options', {})['maxTokens'] = 1024
        print(f'LLM: {old} → typeVersion=1.3, model=claude-sonnet-4-5')
        fixed_llm = True

    # 2. Fix system prompt
    if node.get('type') == '@n8n/n8n-nodes-langchain.agent':
        node['parameters'].setdefault('options', {})['systemMessage'] = NEW_SYSTEM_PROMPT
        print('Agent: system prompt updated')
        fixed_prompt = True

    # 3. Fix guardar_cotizacion: Math.round(m2) + better total parsing + verbose errors
    if node.get('name') == 'Tool guardar_cotizacion':
        node['parameters']['jsCode'] = TOOL_GUARDAR_FIXED
        node['parameters']['description'] = (
            'Guarda la cotización en la base de datos y retorna el número de cotización. '
            'Úsala cuando tengas nombre, RUT, dirección, producto, m² y total del cliente. '
            'IMPORTANTE: después de llamar esta herramienta, copia el campo "mensaje" del resultado '
            'exactamente como está y úsalo como tu respuesta al usuario.'
        )
        print('Tool: guardar_cotizacion code + description updated')
        fixed_tool_desc = True
        fixed_tool_code = True

print(f'\nFixes applied → LLM:{fixed_llm} | Prompt:{fixed_prompt} | ToolCode:{fixed_tool_code}')

# ─── PUT ─────────────────────────────────────────────────────────────────────
result = api_put(WF_ID, wf)
print('PUT OK | nodes:', len(result['nodes']))

# ─── ACTIVATE ────────────────────────────────────────────────────────────────
if not result.get('active'):
    api_post(f'workflows/{WF_ID}/activate')
    print('Activated')
else:
    print('Already active')

# ─── QUICK TEST ──────────────────────────────────────────────────────────────
print('\n--- Quick test ---')
time.sleep(2)
def chat(msg, s):
    b = json.dumps({'message': msg, 'sessionId': s}).encode()
    req = urllib.request.Request('http://localhost:5678/webhook/chat-v2', data=b, method='POST',
                                  headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read()).get('message', '')

s = 'fix-all-test-1'
print('T1:', chat('hola', s))
