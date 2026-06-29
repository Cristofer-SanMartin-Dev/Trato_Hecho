import os
"""
deploy_mcp.py
Crea el workflow "Trato Hecho - MCP" en n8n usando la API tool_use de Claude.
  - Webhook: POST /chat-v2
  - 3 tools: calcular_precio, crear_cotizacion, crear_pago
  - Sin parsing de texto: Claude llama tools nativamente
"""
import urllib.request, urllib.error, json, sys, time, uuid as _uuid

API_KEY  = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODl'
            'hLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJs'
            'aWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkY'
            'mY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_'
            'N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw')
BASE     = 'http://localhost:5678/api/v1'
SUPA_URL = os.environ.get('SUPABASE_URL', '')
SUPA_KEY = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJl'
            'ZiI6ImVucHp4bnR6cGh2ZXpvcGJ4YnR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3'
            'Nzc3MTEzMDUsImV4cCI6MjA5MzI4NzMwNX0.kdT61HJFXFiDXPQUqwZivOmjDFJO3'
            'aoY7XETf_LoZQ4')
TG_CHAT  = '8605918152'

def uid():
    return str(_uuid.uuid4())

def n8n_req(path, method='GET', data=None):
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header('X-N8N-API-KEY', API_KEY)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f'  HTTP {e.code}: {e.read().decode()[:500]}')
        return None
    except Exception as ex:
        print(f'  Error: {ex}')
        return None

def supa_hdrs(extra=None):
    h = [
        {'name': 'apikey',         'value': SUPA_KEY},
        {'name': 'Authorization',  'value': 'Bearer ' + SUPA_KEY},
    ]
    if extra:
        h += extra
    return h

# ─── JavaScript code blocks ───────────────────────────────────────────────────

CODE_EXTRAER = r"""const raw  = $input.first().json;
const body = raw.body || raw;
const uuid = String(body.sessionId || body.uuid || '').trim()
             || 'auto_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
const message = String(body.message || body.chatInput || '').trim();
if (!message) throw new Error('message es requerido');
let bodyHistory = [];
try { if (Array.isArray(body.history)) bodyHistory = body.history; } catch (e) {}
return [{ json: { uuid, message, bodyHistory } }];"""

CODE_CONSTRUIR = r"""const extract = $('Extraer Input').first().json;
const { uuid, message, bodyHistory } = extract;

let history = [];
try {
  const raw = $('GET Historial').first()?.json;
  if (Array.isArray(raw) && raw.length > 0 && Array.isArray(raw[0].messages)) {
    history = raw[0].messages;
  } else if (raw && Array.isArray(raw.messages)) {
    history = raw.messages;
  }
} catch (e) {}
if (!Array.isArray(history) || history.length === 0) {
  if (Array.isArray(bodyHistory)) history = bodyHistory;
}
history = history.filter(m => m && m.content && typeof m.role === 'string');

let quoteCtx = '';
try {
  const raw = $('GET Cotizacion').first()?.json;
  const q = Array.isArray(raw) && raw.length > 0 ? raw[0] : (raw?.numero ? raw : null);
  if (q) {
    quoteCtx = '\n\nCOTIZACION EXISTENTE #' + q.numero
      + ': ' + q.producto + ', ' + q.m2 + ' m2, instalacion='
      + (q.instalacion ? 'SI' : 'NO')
      + ', total=$' + Number(q.total).toLocaleString('es-CL')
      + '. Estado: ' + (q.estado || 'pendiente') + '.';
  }
} catch (e) {}

const systemPrompt = 'Eres Queno, asistente de ventas de Trato Hecho, empresa chilena de pasto artificial en Melipilla.\n\n'
  + 'CATALOGO (precios CLP por m2 con IVA):\n'
  + '- Luxury Emerald (40mm): instalado $12.500/m2, solo pasto $8.500/m2\n'
  + '- Soft Touch (30mm): instalado $10.500/m2, solo pasto $7.000/m2\n'
  + '- Pet-Friendly Turf (35mm): instalado $11.500/m2, solo pasto $7.500/m2\n'
  + '- Pasto Deportivo Futbol 7: $9.500/m2 (instalacion incluida)\n'
  + '- Pasto Deportivo Futbol 11: $8.500/m2 (instalacion incluida)\n'
  + '- Pasto Deportivo Futbol: $9.000/m2 (instalacion incluida)\n'
  + '- Pasto Tenis & Padel: $11.000/m2 (instalacion incluida)\n'
  + 'Instalacion residencial: +$4.500/m2.\n\n'
  + 'PROCESO DE VENTA:\n'
  + '1. Identifica si es jardin residencial o cancha deportiva.\n'
  + '2. Residencial: recomienda producto segun uso -> pregunta m2 -> pregunta instalacion (SI/NO) -> llama calcular_precio de inmediato.\n'
  + '3. Deportivo: identifica tipo de cancha (Futbol 7/11/Tenis/Padel) -> pregunta dimensiones (largo x ancho) -> llama calcular_precio.\n'
  + '4. Tras mostrar precio: ofrece cotizacion formal -> pide nombre, RUT y direccion -> llama crear_cotizacion.\n'
  + '5. Si el cliente quiere pagar: llama crear_pago con numero de cotizacion y monto.\n\n'
  + 'REGLAS CRITICAS:\n'
  + '- NUNCA calcules precios manualmente. Siempre usa calcular_precio.\n'
  + '- Llama calcular_precio EN CUANTO tengas producto y m2 confirmados.\n'
  + '- Solo una pregunta por respuesta. Maximo 4 lineas.\n'
  + '- Responde siempre en espanol.\n'
  + '- No repitas informacion ya entregada en el historial.'
  + quoteCtx;

const tools = [
  {
    name: 'calcular_precio',
    description: 'Calcula el precio exacto segun producto, metros cuadrados e instalacion. Llamar SIEMPRE antes de mostrar precios.',
    input_schema: {
      type: 'object',
      properties: {
        producto: {
          type: 'string',
          enum: ['Luxury Emerald (40mm)', 'Soft Touch (30mm)', 'Pet-Friendly Turf (35mm)',
                 'Pasto Deportivo Futbol 7', 'Pasto Deportivo Futbol 11',
                 'Pasto Deportivo Futbol', 'Pasto Tenis & Padel'],
          description: 'Nombre exacto del producto del catalogo'
        },
        m2:             { type: 'number',  description: 'Metros cuadrados a instalar' },
        con_instalacion: { type: 'boolean', description: 'true si incluye mano de obra de instalacion' }
      },
      required: ['producto', 'm2', 'con_instalacion']
    }
  },
  {
    name: 'crear_cotizacion',
    description: 'Crea y guarda una cotizacion formal. Solo llamar cuando se tengan nombre, RUT y direccion completos.',
    input_schema: {
      type: 'object',
      properties: {
        nombre:          { type: 'string', description: 'Nombre completo del cliente' },
        rut:             { type: 'string', description: 'RUT formato 12.345.678-9' },
        direccion:       { type: 'string', description: 'Direccion completa de instalacion' },
        producto:        { type: 'string', description: 'Nombre exacto del producto' },
        m2:              { type: 'number' },
        con_instalacion: { type: 'boolean' },
        total:           { type: 'number', description: 'Total calculado por calcular_precio. Pasar 0 si no se calculo aun.' }
      },
      required: ['nombre', 'rut', 'direccion', 'producto', 'm2', 'con_instalacion', 'total']
    }
  },
  {
    name: 'crear_pago',
    description: 'Genera link de pago MercadoPago para una cotizacion existente.',
    input_schema: {
      type: 'object',
      properties: {
        numero_cotizacion: { type: 'string', description: 'Numero COT-YYYY-XXXXX' },
        monto:             { type: 'number', description: 'Monto total a cobrar' }
      },
      required: ['numero_cotizacion', 'monto']
    }
  }
];

const messages = history.slice(-20).map(m => ({
  role:    m.role === 'assistant' ? 'assistant' : 'user',
  content: typeof m.content === 'string' ? m.content : JSON.stringify(m.content)
}));
messages.push({ role: 'user', content: message });

const claudeBody = JSON.stringify({
  model:       'claude-sonnet-4-5',
  max_tokens:  1024,
  system:      systemPrompt,
  messages,
  tools,
  tool_choice: { type: 'auto' }
});

return [{ json: { claudeBody, messages, uuid, message, systemPrompt, tools } }];"""

CODE_PARSEAR_V1 = r"""const resp   = $input.first().json;
const prompt = $('Construir Prompt').first().json;

const stopReason = resp.stop_reason;
const content    = Array.isArray(resp.content) ? resp.content : [];

if (stopReason === 'tool_use') {
  const toolBlock = content.find(b => b.type === 'tool_use');
  if (toolBlock) {
    return [{
      json: {
        action:     toolBlock.name,
        toolUseId:  toolBlock.id,
        toolInput:  toolBlock.input,
        rawContent: content,
        messages:   prompt.messages,
        uuid:       prompt.uuid,
        message:    prompt.message
      }
    }];
  }
}

const textBlock    = content.find(b => b.type === 'text');
const textResponse = textBlock ? textBlock.text : 'Lo siento, no pude procesar tu solicitud.';
return [{
  json: {
    action: 'text',
    textResponse,
    rawContent: content,
    messages:   prompt.messages,
    uuid:       prompt.uuid,
    message:    prompt.message
  }
}];"""

CODE_CALCULAR = r"""const data = $input.first().json;
const { producto, m2, con_instalacion } = data.toolInput;
const { toolUseId, rawContent, messages, uuid, message } = data;

const INST = {
  'Luxury Emerald (40mm)':    12500,
  'Soft Touch (30mm)':        10500,
  'Pet-Friendly Turf (35mm)': 11500,
  'Pasto Deportivo Futbol 7':  9500,
  'Pasto Deportivo Futbol 11': 8500,
  'Pasto Deportivo Futbol':    9000,
  'Pasto Tenis & Padel':      11000
};
const PASTO = {
  'Luxury Emerald (40mm)':    8500,
  'Soft Touch (30mm)':        7000,
  'Pet-Friendly Turf (35mm)': 7500
};

const esDeportivo = /Deportivo|Tenis|Padel/.test(producto);
const m2m = Math.ceil(m2 * 1.10);
let total, subP, subI;

if (esDeportivo) {
  total = m2m * (INST[producto] || 9000);
  subP  = total; subI = 0;
} else if (con_instalacion) {
  subP  = m2m * (PASTO[producto] || 7000);
  subI  = m2m * 4500;
  total = m2m * (INST[producto]  || 10500);
} else {
  total = m2m * (PASTO[producto] || 7000);
  subP  = total; subI = 0;
}

const fmt = n => Number(n).toLocaleString('es-CL');
const result = {
  producto, m2_solicitado: m2, m2_con_margen: m2m,
  subtotal_pasto: subP, subtotal_instalacion: subI, total, con_instalacion,
  desglose: subI > 0
    ? 'Pasto: $' + fmt(subP) + ' + Instalacion: $' + fmt(subI) + ' = TOTAL: $' + fmt(total)
    : 'TOTAL: $' + fmt(total)
};

return [{ json: { toolResultContent: JSON.stringify(result), toolUseId, rawContent, messages, uuid, message } }];"""

CODE_PREP_COT = r"""const data = $input.first().json;
const { nombre, rut, direccion, producto, m2, con_instalacion, total } = data.toolInput;
const { toolUseId, rawContent, messages, uuid, message } = data;

const rand = Math.floor(10000 + Math.random() * 90000);
const num  = 'COT-' + new Date().getFullYear() + '-' + rand;

const quote = {
  numero:      num,
  session_id:  uuid,
  nombre, rut, direccion, producto, m2,
  instalacion: con_instalacion,
  total,
  estado:      'pendiente'
};

return [{ json: {
  quote, numero: num, nombre, rut, direccion, producto, m2,
  con_instalacion, total, toolUseId, rawContent, messages, uuid, message
} }];"""

CODE_RESULT_COT = r"""const data = $input.first().json;
const { numero, nombre, rut, direccion, producto, m2,
        con_instalacion, total, toolUseId, rawContent, messages, uuid, message } = data;

const fmt = n => Number(n).toLocaleString('es-CL');
const toolResultContent = JSON.stringify({
  numero, nombre, rut, direccion, producto, m2, con_instalacion, total,
  estado: 'creada',
  mensaje: 'Cotizacion ' + numero + ' creada exitosamente.'
    + (total > 0 ? ' Total: $' + fmt(total) + '.' : '')
    + ' Informa al cliente y ofrece proceder al pago con crear_pago.'
});

return [{ json: { toolResultContent, toolUseId, rawContent, messages, uuid, message } }];"""

CODE_PREP_PAGO = r"""const data = $input.first().json;
const { numero_cotizacion, monto } = data.toolInput;
const { toolUseId, rawContent, messages, uuid, message } = data;

const mpBody = JSON.stringify({
  items: [{
    title:       'Pasto Artificial - Cot. ' + numero_cotizacion,
    description: 'Trato Hecho - Pasto artificial Melipilla',
    quantity:    1,
    currency_id: 'CLP',
    unit_price:  monto
  }],
  external_reference: numero_cotizacion
});

return [{ json: { mpBody, numero_cotizacion, monto, toolUseId, rawContent, messages, uuid, message } }];"""

CODE_RESULT_PAGO = r"""const mpResp = $input.first().json;
const prep   = $('Prep Pago').first().json;
const { toolUseId, rawContent, messages, uuid, message, numero_cotizacion, monto } = prep;

const payLink = mpResp.init_point || mpResp.sandbox_init_point || '';
const toolResultContent = JSON.stringify({
  numero_cotizacion, monto,
  link_pago: payLink || '',
  estado:    payLink ? 'link_generado' : 'pendiente',
  mensaje:   payLink
    ? 'Link de pago listo: ' + payLink + '. Muestra este link al cliente para que complete el pago.'
    : 'No se pudo generar el link. Indica al cliente que nos contacte directamente.'
});

return [{ json: { toolResultContent, toolUseId, rawContent, messages, uuid, message } }];"""

CODE_TOOL_RESULT = r"""const data   = $input.first().json;
const prompt = $('Construir Prompt').first().json;
const { toolResultContent, toolUseId, rawContent, messages, uuid, message } = data;

const updatedMessages = [
  ...messages,
  { role: 'assistant', content: rawContent },
  { role: 'user',      content: [{ type: 'tool_result', tool_use_id: toolUseId, content: toolResultContent }] }
];

const claudeBody = JSON.stringify({
  model:       'claude-sonnet-4-5',
  max_tokens:  1024,
  system:      prompt.systemPrompt,
  messages:    updatedMessages,
  tools:       prompt.tools,
  tool_choice: { type: 'auto' }
});

return [{ json: { claudeBody, updatedMessages, uuid, message } }];"""

CODE_PARSEAR_V2 = r"""const resp    = $input.first().json;
const prev    = $('Tool Result').first().json;
const content = Array.isArray(resp.content) ? resp.content : [];
const txtBlk  = content.find(b => b.type === 'text');
const textResponse = txtBlk ? txtBlk.text : 'Listo! En que mas te puedo ayudar?';
return [{ json: { action: 'tool_result', textResponse, uuid: prev.uuid, message: prev.message } }];"""

CODE_PREP_HIST = r"""const data   = $input.first().json;
const { textResponse, uuid, message } = data;
const prompt = $('Construir Prompt').first().json;
const base   = Array.isArray(prompt.messages) ? prompt.messages : [];

const newHist = [
  ...base,
  { role: 'assistant', content: textResponse }
].slice(-40);

return [{ json: { uuid, history: newHist, message, assistantMsg: textResponse } }];"""

# ─── Helper: standard Claude API HTTP node params ─────────────────────────────

def claude_http_node(name, node_id, position, body_expr='={{ $json.claudeBody }}'):
    return {
        'parameters': {
            'method':              'POST',
            'url':                 'https://api.anthropic.com/v1/messages',
            'authentication':      'genericCredentialType',
            'genericAuthType':     'httpHeaderAuth',
            'sendHeaders':         True,
            'headerParameters': {
                'parameters': [
                    {'name': 'anthropic-version', 'value': '2023-06-01'},
                    {'name': 'content-type',       'value': 'application/json'}
                ]
            },
            'sendBody':    True,
            'specifyBody': 'json',
            'jsonBody':    body_expr,
            'options':     {'timeout': 30000}
        },
        'id':          node_id,
        'name':        name,
        'type':        'n8n-nodes-base.httpRequest',
        'typeVersion':  4.2,
        'position':    position,
        'credentials': {
            'httpHeaderAuth': {'id': 'GoQq4Na0MeD7nLo1', 'name': 'Claude - Trato Hecho'}
        }
    }

def responder_node(name, node_id, position):
    return {
        'parameters': {
            'respondWith':  'json',
            'responseBody': '={{ JSON.stringify({ message: $(\'Preparar Historial\').first().json.assistantMsg, action: \'text\' }) }}',
            'options': {
                'responseHeaders': {
                    'entries': [
                        {'name': 'Access-Control-Allow-Origin', 'value': '*'},
                        {'name': 'Content-Type',                'value': 'application/json'}
                    ]
                }
            }
        },
        'id':          node_id,
        'name':        name,
        'type':        'n8n-nodes-base.respondToWebhook',
        'typeVersion':  1,
        'position':    position
    }

# ─── Node definitions ─────────────────────────────────────────────────────────

N_WEBHOOK    = uid(); N_EXTRAER  = uid(); N_GET_HIST  = uid(); N_GET_COT   = uid()
N_CONSTRUIR  = uid(); N_CLAUDE1  = uid(); N_PARSEAR1  = uid(); N_SWITCH    = uid()
N_CALCULAR   = uid(); N_PREP_COT = uid(); N_GUAR_COT  = uid(); N_TELEGRAM  = uid()
N_RES_COT    = uid(); N_PREP_PAGO= uid(); N_MP        = uid(); N_RES_PAGO  = uid()
N_TOOL_RES   = uid(); N_CLAUDE2  = uid(); N_PARSEAR2  = uid()
N_PREP_HIST  = uid(); N_GUAR_HIST= uid(); N_RESPONDER = uid()

nodes = [
    # 1 ── Webhook
    {
        'parameters': {
            'httpMethod': 'POST', 'path': 'chat-v2',
            'responseMode': 'responseNode',
            'options': {'allowedOrigins': '*'}
        },
        'id': N_WEBHOOK, 'name': 'Webhook Chat v2',
        'type': 'n8n-nodes-base.webhook', 'typeVersion': 2,
        'position': [100, 400],
        'webhookId': uid()
    },
    # 2 ── Extraer Input
    {
        'parameters': {'jsCode': CODE_EXTRAER},
        'id': N_EXTRAER, 'name': 'Extraer Input',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [300, 400]
    },
    # 3 ── GET Historial
    {
        'parameters': {
            'method': 'GET',
            'url': "={{ '" + SUPA_URL + "/rest/v1/historial?session_id=eq.' + $json.uuid + '&select=messages' }}",
            'sendHeaders': True,
            'headerParameters': {'parameters': supa_hdrs()},
            'options': {}
        },
        'id': N_GET_HIST, 'name': 'GET Historial',
        'type': 'n8n-nodes-base.httpRequest', 'typeVersion': 4.2,
        'position': [500, 300]
    },
    # 4 ── GET Cotizacion
    {
        'parameters': {
            'method': 'GET',
            'url': "={{ '" + SUPA_URL + "/rest/v1/cotizaciones?session_id=eq.' + $('Extraer Input').first().json.uuid + '&order=created_at.desc&limit=1&select=*' }}",
            'sendHeaders': True,
            'headerParameters': {'parameters': supa_hdrs()},
            'options': {}
        },
        'id': N_GET_COT, 'name': 'GET Cotizacion',
        'type': 'n8n-nodes-base.httpRequest', 'typeVersion': 4.2,
        'position': [500, 500]
    },
    # 5 ── Construir Prompt
    {
        'parameters': {'jsCode': CODE_CONSTRUIR},
        'id': N_CONSTRUIR, 'name': 'Construir Prompt',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [720, 400]
    },
    # 6 ── Llamar Claude v1
    claude_http_node('Llamar Claude v1', N_CLAUDE1, [940, 400]),
    # 7 ── Parsear v1
    {
        'parameters': {'jsCode': CODE_PARSEAR_V1},
        'id': N_PARSEAR1, 'name': 'Parsear v1',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [1160, 400]
    },
    # 8 ── Switch Tool
    {
        'parameters': {
            'rules': {
                'values': [
                    {
                        'conditions': {
                            'options': {'caseSensitive': True, 'leftValue': '', 'typeValidation': 'strict', 'version': 1},
                            'conditions': [{'leftValue': '={{ $json.action }}', 'rightValue': 'calcular_precio',
                                            'operator': {'type': 'string', 'operation': 'equals'}, 'id': uid()}],
                            'combinator': 'and'
                        }
                    },
                    {
                        'conditions': {
                            'options': {'caseSensitive': True, 'leftValue': '', 'typeValidation': 'strict', 'version': 1},
                            'conditions': [{'leftValue': '={{ $json.action }}', 'rightValue': 'crear_cotizacion',
                                            'operator': {'type': 'string', 'operation': 'equals'}, 'id': uid()}],
                            'combinator': 'and'
                        }
                    },
                    {
                        'conditions': {
                            'options': {'caseSensitive': True, 'leftValue': '', 'typeValidation': 'strict', 'version': 1},
                            'conditions': [{'leftValue': '={{ $json.action }}', 'rightValue': 'crear_pago',
                                            'operator': {'type': 'string', 'operation': 'equals'}, 'id': uid()}],
                            'combinator': 'and'
                        }
                    }
                ]
            },
            'options': {'fallbackOutput': 'extra'}
        },
        'id': N_SWITCH, 'name': 'Switch Tool',
        'type': 'n8n-nodes-base.switch', 'typeVersion': 3,
        'position': [1380, 400]
    },
    # 9 ── Calcular Precio  (switch output 0)
    {
        'parameters': {'jsCode': CODE_CALCULAR},
        'id': N_CALCULAR, 'name': 'Calcular Precio',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [1600, 100]
    },
    # 10 ── Prep Cotizacion  (switch output 1)
    {
        'parameters': {'jsCode': CODE_PREP_COT},
        'id': N_PREP_COT, 'name': 'Prep Cotizacion',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [1600, 320]
    },
    # 11 ── Guardar Cotizacion Supabase
    {
        'parameters': {
            'method': 'POST',
            'url': SUPA_URL + '/rest/v1/cotizaciones',
            'sendHeaders': True,
            'headerParameters': {
                'parameters': supa_hdrs([
                    {'name': 'Content-Type', 'value': 'application/json'},
                    {'name': 'Prefer',       'value': 'return=representation'}
                ])
            },
            'sendBody': True, 'specifyBody': 'json',
            'jsonBody': '={{ JSON.stringify($json.quote) }}',
            'options': {}
        },
        'id': N_GUAR_COT, 'name': 'Guardar Cotizacion',
        'type': 'n8n-nodes-base.httpRequest', 'typeVersion': 4.2,
        'position': [1820, 320]
    },
    # 12 ── Telegram Cotizacion
    {
        'parameters': {
            'chatId': TG_CHAT,
            'text': ("=*Nueva Cotizacion*\n"
                     "N: `{{ $('Prep Cotizacion').first().json.numero }}`\n"
                     "Cliente: {{ $('Prep Cotizacion').first().json.nombre }} - {{ $('Prep Cotizacion').first().json.rut }}\n"
                     "Producto: {{ $('Prep Cotizacion').first().json.producto }} - {{ $('Prep Cotizacion').first().json.m2 }} m2\n"
                     "Instalacion: {{ $('Prep Cotizacion').first().json.con_instalacion ? 'Si' : 'No' }}\n"
                     "Total: ${{ Number($('Prep Cotizacion').first().json.total).toLocaleString('es-CL') }} CLP"),
            'additionalFields': {'parse_mode': 'Markdown'}
        },
        'id': N_TELEGRAM, 'name': 'Telegram Cotizacion',
        'type': 'n8n-nodes-base.telegram', 'typeVersion': 1.2,
        'position': [2040, 320],
        'webhookId': uid(),
        'credentials': {
            'telegramApi': {'id': 'telegram-trato-hecho-001', 'name': 'Telegram Bot - Trato Hecho'}
        }
    },
    # 13 ── Resultado Cotizacion
    {
        'parameters': {'jsCode': CODE_RESULT_COT},
        'id': N_RES_COT, 'name': 'Resultado Cotizacion',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [2260, 320]
    },
    # 14 ── Prep Pago  (switch output 2)
    {
        'parameters': {'jsCode': CODE_PREP_PAGO},
        'id': N_PREP_PAGO, 'name': 'Prep Pago',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [1600, 540]
    },
    # 15 ── Llamar MercadoPago
    {
        'parameters': {
            'method': 'POST',
            'url': 'https://api.mercadopago.com/checkout/preferences',
            'authentication': 'genericCredentialType',
            'genericAuthType': 'httpBearerAuth',
            'sendBody': True, 'specifyBody': 'json',
            'jsonBody': '={{ $json.mpBody }}',
            'options': {'timeout': 15000}
        },
        'id': N_MP, 'name': 'Llamar MercadoPago',
        'type': 'n8n-nodes-base.httpRequest', 'typeVersion': 4.2,
        'position': [1820, 540],
        'credentials': {
            'httpBearerAuth': {'id': 'TeM2S1g4Qzk06fx0', 'name': 'Bearer Auth account'}
        }
    },
    # 16 ── Resultado Pago
    {
        'parameters': {'jsCode': CODE_RESULT_PAGO},
        'id': N_RES_PAGO, 'name': 'Resultado Pago',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [2040, 540]
    },
    # 17 ── Tool Result  (merges Calcular, Resultado Cotizacion, Resultado Pago)
    {
        'parameters': {'jsCode': CODE_TOOL_RESULT},
        'id': N_TOOL_RES, 'name': 'Tool Result',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [2480, 320]
    },
    # 18 ── Llamar Claude v2
    claude_http_node('Llamar Claude v2', N_CLAUDE2, [2700, 320]),
    # 19 ── Parsear v2
    {
        'parameters': {'jsCode': CODE_PARSEAR_V2},
        'id': N_PARSEAR2, 'name': 'Parsear v2',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [2920, 320]
    },
    # 20 ── Preparar Historial  (receives from Switch fallback AND Parsear v2)
    {
        'parameters': {'jsCode': CODE_PREP_HIST},
        'id': N_PREP_HIST, 'name': 'Preparar Historial',
        'type': 'n8n-nodes-base.code', 'typeVersion': 2,
        'position': [1600, 760]
    },
    # 21 ── Guardar Historial Supabase
    {
        'parameters': {
            'method': 'POST',
            'url': SUPA_URL + '/rest/v1/historial',
            'sendHeaders': True,
            'headerParameters': {
                'parameters': supa_hdrs([
                    {'name': 'Content-Type', 'value': 'application/json'},
                    {'name': 'Prefer',       'value': 'resolution=merge-duplicates'}
                ])
            },
            'sendBody': True, 'specifyBody': 'json',
            'jsonBody': '={{ JSON.stringify({ session_id: $json.uuid, messages: $json.history, updated_at: new Date().toISOString() }) }}',
            'options': {}
        },
        'id': N_GUAR_HIST, 'name': 'Guardar Historial',
        'type': 'n8n-nodes-base.httpRequest', 'typeVersion': 4.2,
        'position': [1820, 760]
    },
    # 22 ── Responder Webhook
    responder_node('Responder Webhook', N_RESPONDER, [2040, 760])
]

# ─── Connections ──────────────────────────────────────────────────────────────

def conn(target, idx=0):
    return [{'node': target, 'type': 'main', 'index': idx}]

connections = {
    'Webhook Chat v2':    {'main': [conn('Extraer Input')]},
    'Extraer Input':      {'main': [conn('GET Historial'), conn('GET Cotizacion')]},
    'GET Historial':      {'main': [conn('Construir Prompt')]},
    'GET Cotizacion':     {'main': [conn('Construir Prompt')]},
    'Construir Prompt':   {'main': [conn('Llamar Claude v1')]},
    'Llamar Claude v1':   {'main': [conn('Parsear v1')]},
    'Parsear v1':         {'main': [conn('Switch Tool')]},
    # Switch: 0=calcular_precio  1=crear_cotizacion  2=crear_pago  3=text(extra)
    'Switch Tool': {
        'main': [
            conn('Calcular Precio'),
            conn('Prep Cotizacion'),
            conn('Prep Pago'),
            conn('Preparar Historial')   # fallback/extra = text path
        ]
    },
    'Calcular Precio':       {'main': [conn('Tool Result')]},
    'Prep Cotizacion':       {'main': [conn('Guardar Cotizacion')]},
    'Guardar Cotizacion':    {'main': [conn('Telegram Cotizacion')]},
    'Telegram Cotizacion':   {'main': [conn('Resultado Cotizacion')]},
    'Resultado Cotizacion':  {'main': [conn('Tool Result')]},
    'Prep Pago':             {'main': [conn('Llamar MercadoPago')]},
    'Llamar MercadoPago':    {'main': [conn('Resultado Pago')]},
    'Resultado Pago':        {'main': [conn('Tool Result')]},
    'Tool Result':           {'main': [conn('Llamar Claude v2')]},
    'Llamar Claude v2':      {'main': [conn('Parsear v2')]},
    'Parsear v2':            {'main': [conn('Preparar Historial')]},
    'Preparar Historial':    {'main': [conn('Guardar Historial')]},
    'Guardar Historial':     {'main': [conn('Responder Webhook')]},
}

# ─── Build & deploy ───────────────────────────────────────────────────────────

workflow = {
    'name':        'Trato Hecho - MCP',
    'nodes':       nodes,
    'connections': connections,
    'settings': {
        'executionOrder': 'v1',
        'saveManualExecutions': True
    }
}

print('1. Verificando conexion con n8n...')
info = n8n_req('/workflows?limit=1')
if info is None:
    print('   ERROR: no se puede conectar a n8n. Verifica que este corriendo en localhost:5678')
    sys.exit(1)
print('   OK - n8n responde.')

print('2. Creando workflow "Trato Hecho - MCP"...')
payload = json.dumps(workflow).encode('utf-8')
result  = n8n_req('/workflows', 'POST', payload)
if not result:
    print('   ERROR: no se pudo crear el workflow.')
    sys.exit(1)

WF_ID = result.get('id', '')
print(f'   Workflow creado. ID: {WF_ID}, nodos: {len(result.get("nodes", []))}')

print('3. Activando workflow...')
time.sleep(1)
act = n8n_req(f'/workflows/{WF_ID}/activate', 'POST', b'{}')
if act:
    print('   Activo.')
else:
    print('   [WARN] No se pudo activar automaticamente. Activar manualmente en n8n.')

print('4. Probando con mensaje de prueba...')
time.sleep(2)
test_body = json.dumps({
    'message':   'hola, necesito pasto para mi jardin',
    'sessionId': 'test-mcp-v1-' + str(int(time.time())),
    'history':   []
}).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:5678/webhook/chat-v2', data=test_body, method='POST')
req.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req, timeout=40) as r:
        resp = json.loads(r.read())
        msg  = str(resp.get('message', '(sin respuesta)')).encode('ascii', 'replace').decode()
        act  = resp.get('action', '?')
        print(f'   Respuesta: {msg[:200]}')
        print(f'   Action:    {act}')
        print('\nDeploy MCP exitoso!')
        print(f'Webhook URL: http://localhost:5678/webhook/chat-v2')
        print(f'Workflow ID: {WF_ID}')
except urllib.error.HTTPError as e:
    body = e.read()[:300].decode('ascii', 'replace')
    print(f'   HTTP {e.code}: {body}')
    print(f'\nWorkflow creado (ID: {WF_ID}) pero el test fallo.')
    print('Puede que necesites activarlo manualmente en n8n.')
except Exception as ex:
    print(f'   Error en test: {ex}')
    print(f'\nWorkflow creado (ID: {WF_ID}) - verificar manualmente.')
