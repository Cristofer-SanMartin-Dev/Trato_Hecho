import os
"""
Despliega workflow simplificado:
Webhook → Extraer Input → GET Historial → GET Cotización → Claude API → Guardar Historial → Responder
Claude hace TODO: conversar, calcular, cotizar, indicar pago.
Sin nodos JS intermedios de construcción de prompt.
"""
import urllib.request, json, urllib.error

API_KEY = os.environ.get('N8N_API_KEY', '')
WF_ID   = 'CjS3Gm0863S4j9Ij'
ANON    = os.environ.get('SUPABASE_KEY', '')
SUPA    = os.environ.get('SUPABASE_URL', '')
CLAUDE_CRED_ID = 'GoQq4Na0MeD7nLo1'

# ── System prompt (todo el negocio) ──────────────────────────────────────────
SYSTEM_PROMPT = r"""Eres Queno, vendedor virtual de Césped Sintético ARM en Melipilla, Chile.
Tu objetivo es vender césped sintético, tomar medidas, calcular precios y generar cotizaciones formales.

CATÁLOGO (precios CLP/m2, con IVA):
- Luxury Emerald (40mm): $28.500/m2 — jardín o terraza premium
- Soft Touch (30mm): $22.900/m2 — jardín residencial, suave al tacto
- Pet-Friendly Turf (35mm): $26.000/m2 — jardines con mascotas, fibra antimicrobiana
- Pasto Deportivo Fútbol: precio a cotizar — canchas fútbol 11 y fútbol 7
- Pasto Tenis & Pádel: precio a cotizar — canchas tenis y pádel
- Instalación opcional: +$4.500/m2

CÓMO CALCULAR EL PRECIO (hazlo tú mismo con precisión):
1. m2 solicitados × 1.10 → redondear hacia arriba al entero = m2 con margen técnico
2. m2 con margen × precio/m2 = subtotal pasto
3. Si instalación: m2 con margen × 4.500 = subtotal instalación
4. Total = subtotal pasto + subtotal instalación
Muestra siempre el desglose paso a paso.

FLUJO DE VENTA:
1. Sin producto → pregunta uso (jardín/terraza o cancha deportiva) y muestra opciones con precios
2. Con producto, sin m2 → pregunta cuántos m2 o dimensiones (acepta "5x8", "5 por 8", número solo)
3. Con producto + m2 → calcula y muestra desglose. Luego pregunta: ¿necesita instalación? (+$4.500/m2) SI o NO
4. Con instalación definida → muestra total final. Di: 'Escribe COTIZAR para cotización formal'
5. Cliente escribe COTIZAR → pide nombre completo
6. Tras nombre → pide RUT (formato chileno: 12.345.678-9)
7. Tras RUT → pide dirección de instalación completa
8. Tras dirección → emite ÚNICAMENTE esta etiqueta sin ningún texto antes ni después:
[COTIZAR: nombre=X, rut=X, direccion=X, m2=X, tipo=X, instalacion=SI/NO, total=X]

INTERPRETACIÓN DE MEDIDAS:
- Número solo (20) o con unidad (20m2, 20 metros) = m2 directamente
- Dos números con x/por/* (5x8, 5 por 8, 5*8) = largo × ancho → calcula m2
- EXCEPCIÓN: en modo nombre/RUT/dirección, NUNCA interpretes texto ni números como m2

CUANDO EL CLIENTE NO SABE SUS MEDIDAS:
- Explica brevemente cómo medir (huincha, largo × ancho en metros)
- Agrega al final exactamente: [CALCULAR]

SI HAY COTIZACIÓN EXISTENTE (aparece en el primer mensaje del sistema):
- Muéstrale los datos al cliente
- Ofrece: '¿Quieres proceder al pago?'
- Para iniciar pago usa: [PAGAR: numero=X, monto=X]

REGLAS ESTRICTAS:
- Máximo 4 líneas por respuesta. Solo 1 pregunta por mensaje.
- NUNCA saludar con 'Hola' si ya hay historial de conversación.
- NUNCA reiniciar el flujo si ya hay producto o datos recopilados en el historial.
- NUNCA pedir datos ya entregados en el historial.
- NUNCA calcular precios para productos deportivos (precio a cotizar).
- NUNCA agregar texto antes o después de [COTIZAR:] o [PAGAR:] cuando corresponda.
- No interpretar RUT, teléfono o código postal como metros cuadrados.
- Si el número parece fuera de rango (<1 o >1000 m2), confirma antes de continuar.
- Si el cliente cambia de producto, confirma el cambio explícitamente."""

# ── Nodos ─────────────────────────────────────────────────────────────────────
nodes = [

  # 1. Webhook
  {
    "id": "node-webhook",
    "name": "Webhook Chat",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [0, 300],
    "parameters": {
      "httpMethod": "POST",
      "path": "chat",
      "responseMode": "responseNode",
      "options": {"allowedOrigins": "*"}
    }
  },

  # 2. Extraer Input
  {
    "id": "node-extraer",
    "name": "Extraer Input",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [220, 300],
    "parameters": {
      "jsCode": r"""const raw = $input.first().json;
const body = raw.body || raw;

const uuid = String(body.sessionId || body.uuid || '').trim()
             || 'auto_' + Date.now() + '_' + Math.random().toString(36).substr(2,9);
const message     = String(body.message || body.text || '').trim();
const bodyHistory = Array.isArray(body.history) ? body.history : [];

return [{ json: { uuid, message, bodyHistory } }];"""
    }
  },

  # 3. GET Historial Supabase
  {
    "id": "node-get-historial",
    "name": "GET Historial Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [440, 200],
    "alwaysOutputData": True,
    "onError": "continueRegularOutput",
    "parameters": {
      "method": "GET",
      "url": f"{SUPA}/rest/v1/historial?session_id=eq={{{{$('Extraer Input').first().json.uuid}}}}&select=messages&limit=1",
      "authentication": "none",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [
          {"name": "apikey",         "value": ANON},
          {"name": "Authorization",  "value": f"Bearer {ANON}"}
        ]
      }
    }
  },

  # 4. GET Cotización Supabase
  {
    "id": "node-get-cotizacion",
    "name": "GET Cotización Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [440, 420],
    "alwaysOutputData": True,
    "onError": "continueRegularOutput",
    "parameters": {
      "method": "GET",
      "url": f"{SUPA}/rest/v1/cotizaciones?session_id=eq={{{{$('Extraer Input').first().json.uuid}}}}&select=numero,producto,m2,instalacion,total,estado&order=created_at.desc&limit=1",
      "authentication": "none",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [
          {"name": "apikey",         "value": ANON},
          {"name": "Authorization",  "value": f"Bearer {ANON}"}
        ]
      }
    }
  },

  # 5. Llamar Claude API — con system prompt completo y mensajes desde historial
  {
    "id": "node-claude",
    "name": "Llamar Claude API",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [680, 300],
    "parameters": {
      "method": "POST",
      "url": "https://api.anthropic.com/v1/messages",
      "authentication": "genericCredentialType",
      "genericAuthType": "httpHeaderAuth",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [
          {"name": "anthropic-version", "value": "2023-06-01"},
          {"name": "content-type",      "value": "application/json"}
        ]
      },
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": r"""={{
(function() {
  const extract = $('Extraer Input').first().json;
  const uuid    = extract.uuid;
  const message = extract.message;
  const bodyHistory = extract.bodyHistory || [];

  // Historial desde Supabase (fallback: historial del frontend)
  let history = [];
  try {
    const raw = $('GET Historial Supabase').first().json;
    if (Array.isArray(raw) && raw.length > 0 && Array.isArray(raw[0].messages)) {
      history = raw[0].messages;
    } else if (raw && Array.isArray(raw.messages)) {
      history = raw.messages;
    }
  } catch(e) {}
  if (!Array.isArray(history) || history.length === 0) {
    history = Array.isArray(bodyHistory) ? bodyHistory : [];
  }
  history = history.filter(m => m && m.content);

  // Cotización existente — la inyectamos como primer mensaje del sistema
  let quoteNote = '';
  try {
    const raw = $('GET Cotización Supabase').first().json;
    const q = Array.isArray(raw) && raw.length > 0 ? raw[0]
              : (raw && raw.numero ? raw : null);
    if (q && q.numero) {
      quoteNote = 'CONTEXTO: El cliente ya tiene Cotización #' + q.numero
        + ': ' + q.producto
        + ', ' + q.m2 + ' m²'
        + ', instalacion=' + (q.instalacion ? 'SI' : 'NO')
        + ', total=$' + Number(q.total).toLocaleString('es-CL')
        + '. Estado: ' + q.estado + '.';
    }
  } catch(e) {}

  // Construir array de mensajes para Claude
  const msgs = [
    ...history.map(m => ({
      role: m.role === 'assistant' ? 'assistant' : 'user',
      content: String(m.content)
    })),
    { role: 'user', content: String(message) }
  ];

  // Si hay cotización, la ponemos como primer mensaje de usuario invisible
  if (quoteNote) {
    msgs.unshift({ role: 'user', content: quoteNote });
    msgs.splice(1, 0, { role: 'assistant', content: 'Entendido, tengo el contexto de la cotización.' });
  }

  return JSON.stringify({
    model: 'claude-sonnet-4-5',
    max_tokens: 1024,
    system: """ + json.dumps(SYSTEM_PROMPT) + r""",
    messages: msgs
  });
})()
}}"""
    },
    "credentials": {
      "httpHeaderAuth": {"id": CLAUDE_CRED_ID, "name": "Claude - Trato Hecho"}
    }
  },

  # 6. Parsear Respuesta
  {
    "id": "node-parsear",
    "name": "Parsear Respuesta",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [900, 300],
    "parameters": {
      "jsCode": r"""const resp = $input.first().json;
const rawText = resp?.content?.[0]?.text || resp?.choices?.[0]?.message?.content || '';

// Detectar etiquetas de acción
let action = 'CHAT';
let actionData = {};

const cotizarMatch = rawText.match(/\[COTIZAR:\s*([^\]]+)\]/);
const pagarMatch   = rawText.match(/\[PAGAR:\s*([^\]]+)\]/);

if (cotizarMatch) {
  action = 'COTIZAR';
  cotizarMatch[1].split(',').forEach(pair => {
    const [k, v] = pair.split('=').map(s => s.trim());
    if (k && v !== undefined) actionData[k] = v;
  });
}
if (pagarMatch) {
  action = 'PAGAR';
  pagarMatch[1].split(',').forEach(pair => {
    const [k, v] = pair.split('=').map(s => s.trim());
    if (k && v !== undefined) actionData[k] = v;
  });
}

// Limpiar etiquetas del texto visible
const cleanText = rawText
  .replace(/\[COTIZAR:[^\]]*\]/g, '')
  .replace(/\[PAGAR:[^\]]*\]/g, '')
  .trim();

const uuid = $('Extraer Input').first().json.uuid;

return [{ json: { uuid, rawText, cleanText, action, actionData } }];"""
    }
  },

  # 7. Guardar Historial Supabase
  {
    "id": "node-guardar-historial",
    "name": "Guardar Historial Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1120, 160],
    "onError": "continueRegularOutput",
    "alwaysOutputData": True,
    "parameters": {
      "method": "POST",
      "url": f"{SUPA}/rest/v1/historial",
      "authentication": "none",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [
          {"name": "apikey",         "value": ANON},
          {"name": "Authorization",  "value": f"Bearer {ANON}"},
          {"name": "Content-Type",   "value": "application/json"},
          {"name": "Prefer",         "value": "resolution=merge-duplicates"}
        ]
      },
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": r"""={{
(function() {
  const uuid    = $('Parsear Respuesta').first().json.uuid;
  const userMsg = $('Extraer Input').first().json.message;
  const botMsg  = $('Parsear Respuesta').first().json.cleanText;

  // Leer historial previo
  let history = [];
  try {
    const raw = $('GET Historial Supabase').first().json;
    if (Array.isArray(raw) && raw.length > 0 && Array.isArray(raw[0].messages)) {
      history = raw[0].messages;
    }
  } catch(e) {}
  if (!Array.isArray(history)) history = [];
  history = history.filter(m => m && m.content);

  history.push({ role: 'user',      content: userMsg });
  history.push({ role: 'assistant', content: botMsg  });
  history = history.slice(-40); // max 20 turnos

  return JSON.stringify({
    session_id: uuid,
    messages: history,
    updated_at: new Date().toISOString()
  });
})()
}}"""
    }
  },

  # 8. Guardar Cotización Supabase (solo si action=COTIZAR)
  {
    "id": "node-guardar-cotizacion",
    "name": "Guardar Cotización Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1120, 380],
    "onError": "continueRegularOutput",
    "alwaysOutputData": True,
    "parameters": {
      "method": "POST",
      "url": f"{SUPA}/rest/v1/cotizaciones",
      "authentication": "none",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [
          {"name": "apikey",         "value": ANON},
          {"name": "Authorization",  "value": f"Bearer {ANON}"},
          {"name": "Content-Type",   "value": "application/json"},
          {"name": "Prefer",         "value": "resolution=merge-duplicates"}
        ]
      },
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": r"""={{
(function() {
  const p = $('Parsear Respuesta').first().json;
  const d = p.actionData || {};
  const year = new Date().getFullYear();
  const seq  = String(Date.now()).slice(-5);
  return JSON.stringify({
    session_id:  p.uuid,
    numero:      'COT-' + year + '-' + seq,
    nombre:      d.nombre || '',
    rut:         d.rut    || '',
    direccion:   d.direccion || '',
    producto:    d.tipo   || '',
    m2:          parseFloat(d.m2) || 0,
    instalacion: String(d.instalacion || '').toUpperCase() === 'SI',
    total:       parseFloat(String(d.total || '0').replace(/[^0-9.]/g, '')) || 0,
    estado:      'pendiente',
    created_at:  new Date().toISOString()
  });
})()
}}"""
    }
  },

  # 9. Responder Webhook
  {
    "id": "node-responder",
    "name": "Responder Webhook",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [1360, 300],
    "parameters": {
      "respondWith": "json",
      "responseBody": r"""={{
(function() {
  const p = $('Parsear Respuesta').first().json;
  return {
    message:     p.cleanText || '',
    action:      p.action    || 'CHAT',
    actionData:  p.actionData || {},
    quote:       null,
    paymentLink: null
  };
})()
}}"""
    }
  }
]

# ── Conexiones ────────────────────────────────────────────────────────────────
connections = {
  "Webhook Chat": {
    "main": [[{"node": "Extraer Input", "type": "main", "index": 0}]]
  },
  "Extraer Input": {
    "main": [[
      {"node": "GET Historial Supabase",  "type": "main", "index": 0},
      {"node": "GET Cotización Supabase", "type": "main", "index": 0}
    ]]
  },
  "GET Historial Supabase": {
    "main": [[{"node": "Llamar Claude API", "type": "main", "index": 0}]]
  },
  "GET Cotización Supabase": {
    "main": [[{"node": "Llamar Claude API", "type": "main", "index": 0}]]
  },
  "Llamar Claude API": {
    "main": [[{"node": "Parsear Respuesta", "type": "main", "index": 0}]]
  },
  "Parsear Respuesta": {
    "main": [[
      {"node": "Guardar Historial Supabase",  "type": "main", "index": 0},
      {"node": "Guardar Cotización Supabase", "type": "main", "index": 0},
      {"node": "Responder Webhook",           "type": "main", "index": 0}
    ]]
  },
  "Guardar Historial Supabase":  {"main": [[]]},
  "Guardar Cotización Supabase": {"main": [[]]},
}

# ── Deploy ────────────────────────────────────────────────────────────────────
def n8n(path, method='GET', data=None):
    req = urllib.request.Request(f'http://localhost:5678/api/v1{path}', data=data, method=method)
    req.add_header('X-N8N-API-KEY', API_KEY)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f'  HTTP {e.code}: {e.read().decode()[:300]}')
        return None

print('1. Desactivando workflow...')
n8n(f'/workflows/{WF_ID}/deactivate', 'POST', b'{}')

print('2. Actualizando workflow...')
payload = json.dumps({
    'name': 'Trato Hecho - Chat Agent (Simple)',
    'nodes': nodes,
    'connections': connections,
    'settings': {'executionOrder': 'v1'}
}).encode('utf-8')

result = n8n(f'/workflows/{WF_ID}', 'PUT', payload)
if result:
    print(f'   OK. Nodos: {len(result["nodes"])}')
else:
    print('   ERROR en PUT')
    exit(1)

print('3. Reactivando...')
n8n(f'/workflows/{WF_ID}/activate', 'POST', b'{}')

print('4. Probando webhook...')
test_body = json.dumps({'message': 'hola', 'sessionId': 'test-simple-v1', 'history': []}).encode()
req = urllib.request.Request('http://localhost:5678/webhook/chat', data=test_body, method='POST')
req.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
        print(f'   message: {resp.get("message","(FALTA)")[:100]}')
        print(f'   action:  {resp.get("action")}')
except Exception as ex:
    print(f'   ERROR: {ex}')

print('\nListo.')
