"""
Reconstruye el workflow simplificado usando los UUIDs originales del backup
para que n8n registre correctamente el webhook.
"""
import urllib.request, json, urllib.error, time, uuid

KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'
WF_ID   = 'CjS3Gm0863S4j9Ij'
ANON    = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVucHp4bnR6cGh2ZXpvcGJ4YnR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc3MTEzMDUsImV4cCI6MjA5MzI4NzMwNX0.kdT61HJFXFiDXPQUqwZivOmjDFJO3aoY7XETf_LoZQ4'
SUPA    = 'https://enpzxntzphvezopbxbtx.supabase.co'
CLAUDE_CRED_ID = 'GoQq4Na0MeD7nLo1'

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

# Leer backup para obtener UUIDs originales de los nodos que reutilizamos
with open('n8n/workflow_backup.json', encoding='utf-8') as f:
    backup = json.load(f)

orig_ids = {n['name']: n['id'] for n in backup['nodes']}
print('IDs originales disponibles:', list(orig_ids.keys()))

# Para nodos nuevos, generamos UUIDs frescos
def get_id(name):
    return orig_ids.get(name, str(uuid.uuid4()))

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres Queno, vendedor virtual de Césped Sintético ARM en Melipilla, Chile.
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

SI HAY COTIZACIÓN EXISTENTE (aparece al inicio del contexto):
- Muéstrale los datos al cliente
- Ofrece: '¿Quieres proceder al pago?'
- Para iniciar pago usa: [PAGAR: numero=X, monto=X]

REGLAS ESTRICTAS:
- Máximo 4 líneas por respuesta. Solo 1 pregunta por mensaje.
- NUNCA saludar con 'Hola' si ya hay historial de conversación.
- NUNCA reiniciar el flujo si ya hay producto o datos en el historial.
- NUNCA pedir datos ya entregados en el historial.
- NUNCA calcular precios para productos deportivos (precio a cotizar).
- NUNCA agregar texto antes o después de [COTIZAR:] o [PAGAR:] cuando corresponda.
- No interpretar RUT, teléfono o código postal como metros cuadrados.
- Si el número parece fuera de rango (<1 o >1000 m2), confirma antes de continuar.
- Si el cliente cambia de producto, confirma el cambio explícitamente."""

# Escapar para usar dentro de expresión JS en n8n
SYSTEM_ESCAPED = json.dumps(SYSTEM_PROMPT)  # produce "..." con comillas y escapes

# ── Definición de nodos con UUIDs correctos ────────────────────────────────────
nodes = [

  {
    "id": get_id("Webhook Chat"),
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

  {
    "id": get_id("Extraer Input"),
    "name": "Extraer Input",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [220, 300],
    "parameters": {
      "jsCode": (
        "const raw = $input.first().json;\n"
        "const body = raw.body || raw;\n"
        "const uuid = String(body.sessionId || body.uuid || '').trim()\n"
        "             || 'auto_' + Date.now() + '_' + Math.random().toString(36).substr(2,9);\n"
        "const message     = String(body.message || body.text || '').trim();\n"
        "const bodyHistory = Array.isArray(body.history) ? body.history : [];\n"
        "return [{ json: { uuid, message, bodyHistory } }];"
      )
    }
  },

  {
    "id": get_id("GET Historial Supabase"),
    "name": "GET Historial Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [440, 160],
    "alwaysOutputData": True,
    "onError": "continueRegularOutput",
    "parameters": {
      "method": "GET",
      "url": SUPA + "/rest/v1/historial?session_id=eq={{ $('Extraer Input').first().json.uuid }}&select=messages&limit=1",
      "authentication": "none",
      "sendHeaders": True,
      "headerParameters": {"parameters": [
        {"name": "apikey",        "value": ANON},
        {"name": "Authorization", "value": "Bearer " + ANON}
      ]}
    }
  },

  {
    "id": get_id("GET Cotización Supabase"),
    "name": "GET Cotización Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [440, 440],
    "alwaysOutputData": True,
    "onError": "continueRegularOutput",
    "parameters": {
      "method": "GET",
      "url": SUPA + "/rest/v1/cotizaciones?session_id=eq={{ $('Extraer Input').first().json.uuid }}&select=numero,producto,m2,instalacion,total,estado&order=created_at.desc&limit=1",
      "authentication": "none",
      "sendHeaders": True,
      "headerParameters": {"parameters": [
        {"name": "apikey",        "value": ANON},
        {"name": "Authorization", "value": "Bearer " + ANON}
      ]}
    }
  },

  {
    "id": get_id("Llamar Claude API"),
    "name": "Llamar Claude API",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [700, 300],
    "parameters": {
      "method": "POST",
      "url": "https://api.anthropic.com/v1/messages",
      "authentication": "genericCredentialType",
      "genericAuthType": "httpHeaderAuth",
      "sendHeaders": True,
      "headerParameters": {"parameters": [
        {"name": "anthropic-version", "value": "2023-06-01"},
        {"name": "content-type",      "value": "application/json"}
      ]},
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": (
        "={{\n"
        "(function() {\n"
        "  const extract = $('Extraer Input').first().json;\n"
        "  const message = extract.message;\n"
        "  const bodyHistory = extract.bodyHistory || [];\n"
        "\n"
        "  // Historial desde Supabase (fallback: historial del frontend)\n"
        "  let history = [];\n"
        "  try {\n"
        "    const raw = $('GET Historial Supabase').first().json;\n"
        "    if (Array.isArray(raw) && raw.length > 0 && Array.isArray(raw[0].messages)) {\n"
        "      history = raw[0].messages;\n"
        "    } else if (raw && Array.isArray(raw.messages)) {\n"
        "      history = raw.messages;\n"
        "    }\n"
        "  } catch(e) {}\n"
        "  if (!Array.isArray(history) || history.length === 0) {\n"
        "    history = Array.isArray(bodyHistory) ? bodyHistory : [];\n"
        "  }\n"
        "  history = history.filter(m => m && m.content);\n"
        "\n"
        "  // Cotización existente\n"
        "  let quoteNote = '';\n"
        "  try {\n"
        "    const raw = $('GET Cotización Supabase').first().json;\n"
        "    const q = Array.isArray(raw) && raw.length > 0 ? raw[0]\n"
        "              : (raw && raw.numero ? raw : null);\n"
        "    if (q && q.numero) {\n"
        "      quoteNote = 'CONTEXTO: Cotización #' + q.numero\n"
        "        + ': ' + q.producto\n"
        "        + ', ' + q.m2 + ' m\\u00b2'\n"
        "        + ', instalacion=' + (q.instalacion ? 'SI' : 'NO')\n"
        "        + ', total=$' + Number(q.total).toLocaleString('es-CL')\n"
        "        + '. Estado: ' + q.estado;\n"
        "    }\n"
        "  } catch(e) {}\n"
        "\n"
        "  // Construir mensajes\n"
        "  const msgs = [\n"
        "    ...history.map(m => ({\n"
        "      role: m.role === 'assistant' ? 'assistant' : 'user',\n"
        "      content: String(m.content)\n"
        "    })),\n"
        "    { role: 'user', content: String(message) }\n"
        "  ];\n"
        "\n"
        "  // Inyectar cotización como contexto inicial si existe\n"
        "  if (quoteNote) {\n"
        "    msgs.unshift({ role: 'user', content: quoteNote });\n"
        "    msgs.splice(1, 0, { role: 'assistant', content: 'Entendido.' });\n"
        "  }\n"
        "\n"
        "  return JSON.stringify({\n"
        "    model: 'claude-sonnet-4-5',\n"
        "    max_tokens: 1024,\n"
        "    system: " + SYSTEM_ESCAPED + ",\n"
        "    messages: msgs\n"
        "  });\n"
        "})()\n"
        "}}"
      )
    },
    "credentials": {
      "httpHeaderAuth": {"id": CLAUDE_CRED_ID, "name": "Claude - Trato Hecho"}
    }
  },

  {
    "id": get_id("Parsear Respuesta Claude"),
    "name": "Parsear Respuesta",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [940, 300],
    "parameters": {
      "jsCode": (
        "const resp = $input.first().json;\n"
        "const rawText = resp?.content?.[0]?.text || '';\n"
        "\n"
        "let action = 'CHAT';\n"
        "let actionData = {};\n"
        "\n"
        "const cotizarMatch = rawText.match(/\\[COTIZAR:\\s*([^\\]]+)\\]/);\n"
        "const pagarMatch   = rawText.match(/\\[PAGAR:\\s*([^\\]]+)\\]/);\n"
        "\n"
        "if (cotizarMatch) {\n"
        "  action = 'COTIZAR';\n"
        "  cotizarMatch[1].split(',').forEach(pair => {\n"
        "    const [k, v] = pair.split('=').map(s => s.trim());\n"
        "    if (k && v !== undefined) actionData[k] = v;\n"
        "  });\n"
        "}\n"
        "if (pagarMatch) {\n"
        "  action = 'PAGAR';\n"
        "  pagarMatch[1].split(',').forEach(pair => {\n"
        "    const [k, v] = pair.split('=').map(s => s.trim());\n"
        "    if (k && v !== undefined) actionData[k] = v;\n"
        "  });\n"
        "}\n"
        "\n"
        "const cleanText = rawText\n"
        "  .replace(/\\[COTIZAR:[^\\]]*\\]/g, '')\n"
        "  .replace(/\\[PAGAR:[^\\]]*\\]/g, '')\n"
        "  .trim();\n"
        "\n"
        "const uuid = $('Extraer Input').first().json.uuid;\n"
        "\n"
        "return [{ json: { uuid, rawText, cleanText, action, actionData } }];"
      )
    }
  },

  {
    "id": get_id("Guardar Historial Supabase"),
    "name": "Guardar Historial Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1180, 160],
    "onError": "continueRegularOutput",
    "alwaysOutputData": True,
    "parameters": {
      "method": "POST",
      "url": SUPA + "/rest/v1/historial",
      "authentication": "none",
      "sendHeaders": True,
      "headerParameters": {"parameters": [
        {"name": "apikey",        "value": ANON},
        {"name": "Authorization", "value": "Bearer " + ANON},
        {"name": "Content-Type",  "value": "application/json"},
        {"name": "Prefer",        "value": "resolution=merge-duplicates"}
      ]},
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": (
        "={{\n"
        "(function() {\n"
        "  const uuid    = $('Parsear Respuesta').first().json.uuid;\n"
        "  const userMsg = $('Extraer Input').first().json.message;\n"
        "  const botMsg  = $('Parsear Respuesta').first().json.cleanText;\n"
        "  let history = [];\n"
        "  try {\n"
        "    const raw = $('GET Historial Supabase').first().json;\n"
        "    if (Array.isArray(raw) && raw.length > 0 && Array.isArray(raw[0].messages)) {\n"
        "      history = raw[0].messages;\n"
        "    }\n"
        "  } catch(e) {}\n"
        "  if (!Array.isArray(history)) history = [];\n"
        "  history = history.filter(m => m && m.content);\n"
        "  history.push({ role: 'user',      content: userMsg });\n"
        "  history.push({ role: 'assistant', content: botMsg  });\n"
        "  history = history.slice(-40);\n"
        "  return JSON.stringify({\n"
        "    session_id: uuid,\n"
        "    messages:   history,\n"
        "    updated_at: new Date().toISOString()\n"
        "  });\n"
        "})()\n"
        "}}"
      )
    }
  },

  {
    "id": get_id("Guardar Cotización Supabase"),
    "name": "Guardar Cotización Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1180, 440],
    "onError": "continueRegularOutput",
    "alwaysOutputData": True,
    "parameters": {
      "method": "POST",
      "url": SUPA + "/rest/v1/cotizaciones",
      "authentication": "none",
      "sendHeaders": True,
      "headerParameters": {"parameters": [
        {"name": "apikey",        "value": ANON},
        {"name": "Authorization", "value": "Bearer " + ANON},
        {"name": "Content-Type",  "value": "application/json"},
        {"name": "Prefer",        "value": "resolution=merge-duplicates"}
      ]},
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": (
        "={{\n"
        "(function() {\n"
        "  const p = $('Parsear Respuesta').first().json;\n"
        "  if (p.action !== 'COTIZAR') return JSON.stringify({ session_id: p.uuid, _skip: true });\n"
        "  const d = p.actionData || {};\n"
        "  const year = new Date().getFullYear();\n"
        "  const seq  = String(Date.now()).slice(-5);\n"
        "  return JSON.stringify({\n"
        "    session_id:  p.uuid,\n"
        "    numero:      'COT-' + year + '-' + seq,\n"
        "    nombre:      d.nombre    || '',\n"
        "    rut:         d.rut       || '',\n"
        "    direccion:   d.direccion || '',\n"
        "    producto:    d.tipo      || '',\n"
        "    m2:          parseFloat(d.m2) || 0,\n"
        "    instalacion: String(d.instalacion || '').toUpperCase() === 'SI',\n"
        "    total:       parseFloat(String(d.total || '0').replace(/[^0-9.]/g, '')) || 0,\n"
        "    estado:      'pendiente',\n"
        "    created_at:  new Date().toISOString()\n"
        "  });\n"
        "})()\n"
        "}}"
      )
    }
  },

  {
    "id": get_id("Responder Webhook (Simple)"),
    "name": "Responder Webhook",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [1420, 300],
    "parameters": {
      "respondWith": "json",
      "responseBody": (
        "={{\n"
        "JSON.stringify({\n"
        "  message:    $('Parsear Respuesta').first().json.cleanText || '',\n"
        "  action:     $('Parsear Respuesta').first().json.action    || 'CHAT',\n"
        "  actionData: $('Parsear Respuesta').first().json.actionData || {},\n"
        "  quote:       null,\n"
        "  paymentLink: null\n"
        "})\n"
        "}}"
      )
    }
  }

]

# ── Conexiones ─────────────────────────────────────────────────────────────────
connections = {
  "Webhook Chat": {
    "main": [[
      {"node": "Extraer Input", "type": "main", "index": 0}
    ]]
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

# ── Deploy ─────────────────────────────────────────────────────────────────────
print('Node IDs usados:')
for n in nodes:
    print(f'  {n["id"]} | {n["name"]}')

n8n(f'/workflows/{WF_ID}/deactivate', 'POST', b'{}')
print('\nDesactivado.')

payload = json.dumps({
    'name': 'Trato Hecho - Chat Agent (Simple)',
    'nodes': nodes,
    'connections': connections,
    'settings': {'executionOrder': 'v1'}
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
test = json.dumps({'message': 'hola', 'sessionId': 'test-uuid-fix', 'history': []}).encode()
req = urllib.request.Request('http://localhost:5678/webhook/chat', data=test, method='POST')
req.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req, timeout=35) as r:
        resp = json.loads(r.read())
        print('\nmessage:', resp.get('message','(FALTA)')[:120])
        print('action:', resp.get('action'))
except urllib.error.HTTPError as e:
    print('\nHTTP error:', e.code, e.read()[:200].decode())
except Exception as ex:
    print('\nError:', ex)
