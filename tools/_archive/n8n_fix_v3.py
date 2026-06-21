import os
"""
Fix v3: Integración Mercado Pago — link de pago real con botón en el chat.
Aplica sobre el workflow existente (fix_v2 ya desplegado).

Cambios:
  1. Tool generar_pago → emite marker [PAGAR_MP: numero=X, total=N]
  2. Nuevo nodo "Generar Pago MP" (Code regular, tiene helpers) → llama API MP → [PAYMENT_URL:url]
  3. Actualiza PAGAR rule del system prompt para incluir el total
  4. Conexiones: Guardar Supabase → Generar Pago MP → Responder Webhook
"""
import urllib.request, json, uuid

API   = 'http://localhost:5678/api/v1'
KEY   = os.environ.get('N8N_API_KEY', '')
WF_ID = '4K4vFiRWRG63N92B'

# ─── Tool generar_pago v3 ─────────────────────────────────────────────────────
# toolCode sandbox NO tiene fetch/http → solo emite marker para el nodo siguiente
TOOL_PAGO_V3 = r"""let inp = {};
try {
  if (typeof query !== 'undefined' && query) {
    inp = (typeof query === 'string') ? JSON.parse(query) : query;
  } else {
    const raw = $input.first().json;
    const q = raw.query || raw;
    inp = (typeof q === 'string') ? JSON.parse(q) : q;
  }
} catch(e) { inp = {}; }

const numero = String(inp.numero_cotizacion || inp.numero || '').trim();
const total  = parseInt(String(inp.total || '0').replace(/[^0-9]/g, '')) || 0;

if (!numero || total <= 0) {
  return 'Para procesar el pago necesito el número de cotización y el monto total. ¿Puedes confirmarlos?';
}

return '[PAGAR_MP: numero=' + numero + ', total=' + total + ']';
"""

TOOL_PAGO_V3_DESC = (
    'Genera el link de pago Mercado Pago para una cotización. '
    'Llámala cuando el cliente escriba PAGAR o quiera pagar. '
    'Pasa numero_cotizacion (ej: COT-2026-39293) y total (número entero sin puntos ni $, ej: 825000). '
    'CRÍTICO: La herramienta retorna una cadena. Cópiala literalmente como tu respuesta completa, sin agregar nada.'
)

# ─── Nodo "Generar Pago MP" ───────────────────────────────────────────────────
# Nodo Code REGULAR (no toolCode) → this.helpers.httpRequest SÍ funciona aquí
# IMPORTANTE: en n8n el body debe ser objeto JS (no JSON.stringify), n8n lo serializa solo
MP_NODE_CODE = r"""const agentOutput = $input.first().json;
const message = String(agentOutput.output || '');

// Solo actuar si hay marker de pago emitido por Tool generar_pago
const pagoMatch = message.match(/\[PAGAR_MP:\s*numero=([^,\]]+),\s*total=(\d+)\]/);
if (!pagoMatch) {
  return [{ json: agentOutput }];
}

const numero   = pagoMatch[1].trim();
const total    = parseInt(pagoMatch[2]);
const MP_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN', '');
const FRONTEND = 'http://127.0.0.1:9000';

const fmt = n => Number(n).toLocaleString('es-CL');

let paymentUrl = '';
let mpError    = '';
try {
  // json:true → n8n serializa el body como JSON y parsea la respuesta
  const resp = await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://api.mercadopago.com/checkout/preferences',
    headers: {
      'Authorization': 'Bearer ' + MP_TOKEN
    },
    json: true,
    body: {
      items: [{
        id: numero,
        title: 'Cotizacion ' + numero + ' - Cesped Sintetico ARM',
        quantity: 1,
        unit_price: total,
        currency_id: 'CLP'
      }],
      external_reference: numero
    }
  });

  // En modo test usar sandbox_init_point, en producción usar init_point
  paymentUrl = (resp.sandbox_init_point || resp.init_point || '').trim();
} catch(e) {
  mpError = String(e.message || e);
  console.error('MP Error:', mpError);
}

let newOutput;
if (paymentUrl) {
  newOutput = '💳 Tu link de pago está listo.\n'
            + '🛒 ' + numero + '  |  💰 $' + fmt(total) + '\n\n'
            + '[PAYMENT_URL:' + paymentUrl + ']';
} else {
  newOutput = '💳 Pago para ' + numero + ' por $' + fmt(total) + '.\n\n'
            + 'Hubo un inconveniente generando el link (err: ' + mpError.slice(0,80) + ').\n'
            + 'Un asesor te contactará a la brevedad.';
}

return [{ json: { ...agentOutput, output: newOutput, _mp_url: paymentUrl, _mp_err: mpError } }];
"""

# ─── Helpers ──────────────────────────────────────────────────────────────────
def api_get(path):
    req = urllib.request.Request(f'{API}/{path}', headers={'X-N8N-API-KEY': KEY})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def api_put(wf_id, wf):
    ALLOWED = {'executionOrder', 'callerPolicy', 'saveDataSuccessExecution',
               'saveDataErrorExecution', 'saveManualExecutions', 'timezone',
               'errorWorkflow', 'saveExecutionProgress'}
    body = {
        'name': wf['name'],
        'nodes': wf['nodes'],
        'connections': wf['connections'],
        'settings': {k: v for k, v in wf.get('settings', {}).items() if k in ALLOWED},
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

# ─── GET workflow ──────────────────────────────────────────────────────────────
wf = api_get(f'workflows/{WF_ID}')
print('Got workflow:', wf['name'], '| nodes:', len(wf['nodes']))

# ─── PATCH nodes ──────────────────────────────────────────────────────────────
MP_NODE_ID     = str(uuid.uuid4())
mp_node_exists = False

for node in wf['nodes']:

    # 1. Actualizar Tool generar_pago
    if node.get('name') == 'Tool generar_pago':
        node['parameters']['jsCode'] = TOOL_PAGO_V3
        node['parameters']['description'] = TOOL_PAGO_V3_DESC
        print('✓ Tool generar_pago: actualizado → emite [PAGAR_MP:] marker')

    # 2. Actualizar Generar Pago MP si ya existe
    if node.get('name') == 'Generar Pago MP':
        node['parameters']['jsCode'] = MP_NODE_CODE
        MP_NODE_ID = node['id']
        mp_node_exists = True
        print('✓ Generar Pago MP: actualizado (nodo existente)')

    # 3. Actualizar system prompt: PAGAR debe incluir total
    if node.get('type') == '@n8n/n8n-nodes-langchain.agent':
        prompt = node['parameters'].get('options', {}).get('systemMessage', '')
        old_rule = 'Si el cliente escribe PAGAR y ya hay cotización: llama generar_pago con el número de cotización.'
        new_rule = ('Si el cliente escribe PAGAR y hay una cotización en el historial: '
                    'llama generar_pago pasando numero_cotizacion (ej: COT-2026-XXXXX) '
                    'y total (número entero sin puntos ni $, ej: 825000).')
        if old_rule in prompt:
            node['parameters']['options']['systemMessage'] = prompt.replace(old_rule, new_rule)
            print('✓ System prompt: regla PAGAR actualizada (incluye total)')
        else:
            print('  System prompt: regla PAGAR no encontrada (puede ya estar actualizada)')

# 4. Agregar nodo Generar Pago MP si no existe
if not mp_node_exists:
    sb_pos = [215, 300]
    for node in wf['nodes']:
        if node.get('name') == 'Guardar en Supabase':
            sb_pos = node.get('position', [215, 300])
            break
    wf['nodes'].append({
        'id': MP_NODE_ID,
        'name': 'Generar Pago MP',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [sb_pos[0] + 260, sb_pos[1]],
        'parameters': {
            'jsCode': MP_NODE_CODE,
            'mode': 'runOnceForAllItems'
        }
    })
    print('✓ Generar Pago MP: nuevo nodo agregado')

# ─── UPDATE connections ────────────────────────────────────────────────────────
# Nueva cadena: Guardar en Supabase → Generar Pago MP → Responder Webhook
conns = wf['connections']

sb_main = conns.get('Guardar en Supabase', {}).get('main', [[]])[0]
sb_main = [c for c in sb_main if c.get('node') != 'Responder Webhook']
if not any(c.get('node') == 'Generar Pago MP' for c in sb_main):
    sb_main.append({'node': 'Generar Pago MP', 'type': 'main', 'index': 0})
conns['Guardar en Supabase'] = {'main': [sb_main]}

conns['Generar Pago MP'] = {
    'main': [[{'node': 'Responder Webhook', 'type': 'main', 'index': 0}]]
}
print('✓ Connections: Guardar Supabase → Generar Pago MP → Responder Webhook')

# ─── DEPLOY ───────────────────────────────────────────────────────────────────
result = api_put(WF_ID, wf)
print(f'\nPUT OK | nodes: {len(result["nodes"])} | active: {result.get("active")}')

if not result.get('active'):
    api_post(f'workflows/{WF_ID}/activate')
    print('Activated')

print('\n✅ Fix v3 desplegado. Prueba: genera una cotización y luego escribe PAGAR.')
