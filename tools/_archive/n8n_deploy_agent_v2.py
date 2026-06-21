import os
"""
Deploy: Trato Hecho - AI Agent v2
Nueva arquitectura: Webhook → Extraer → AI Agent (Claude + Memory + Tools) → Responder
Path nuevo: /webhook/chat-v2 (no toca el workflow actual)
"""
import urllib.request, urllib.error, json, uuid

KEY = os.environ.get('N8N_API_KEY', '')
ANTHROPIC_CRED_ID = '4srMm96jg0ztawMd'
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

def n8n(path, method='GET', payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request('http://localhost:5678/api/v1' + path, data=data, method=method)
    req.add_header('X-N8N-API-KEY', KEY)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f'HTTP {e.code}:', e.read().decode()[:600])
        return None

# ─── SYSTEM PROMPT ──────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres Queno, asesor virtual de Césped Sintético ARM en Melipilla, Chile.
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
10. Dirección obtenida → llama guardar_cotizacion con todos los datos

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

# ─── TOOL: calcular_precio ───────────────────────────────────────────────────
TOOL_CALCULAR = """
const inp = $input.first().json;
const producto = String(inp.producto || '').toLowerCase();
const m2 = parseFloat(inp.m2) || 0;
const conInst = inp.con_instalacion === true || inp.con_instalacion === 'true' || inp.con_instalacion === 'SI';

const PRECIOS = {
  'luxury': 28500,
  'emerald': 28500,
  'soft touch': 22900,
  'soft': 22900,
  'pet': 26000,
  'friendly': 26000,
};

let precioPorM2 = 0;
for (const [key, price] of Object.entries(PRECIOS)) {
  if (producto.includes(key)) { precioPorM2 = price; break; }
}

if (m2 <= 0) {
  return [{ json: { error: 'Se necesitan los m² para calcular' } }];
}
if (precioPorM2 === 0) {
  return [{ json: { resultado: 'Producto deportivo — precio a cotizar según especificaciones técnicas' } }];
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
    resumen: `${inp.producto} — $${fmt(precioPorM2)}/m²\\nSuperficie: ${m2} m² → ${m2Margen} m² (con margen técnico 10%)\\nSubtotal pasto: $${fmt(subtotalPasto)}${conInst ? `\\nInstalación: $${fmt(subtotalInst)}` : '\\nInstalación: no incluida'}\\nTOTAL: $${fmt(total)}`
  }
}];
""".strip()

# ─── TOOL: guardar_cotizacion ────────────────────────────────────────────────
TOOL_GUARDAR = f"""
const inp = $input.first().json;
const SUPABASE_URL = '{SUPABASE_URL}';
const SUPABASE_KEY = '{SUPABASE_KEY}';

const year = new Date().getFullYear();
const seq = String(Date.now()).slice(-5);
const numero = 'COT-' + year + '-' + seq;

const total = parseInt(String(inp.total || '0').replace(/[$.,\\s]/g, '')) || 0;
const quote = {{
  numero,
  session_id: String(inp.session_id || ''),
  nombre: String(inp.nombre || ''),
  rut: String(inp.rut || ''),
  direccion: String(inp.direccion || ''),
  producto: String(inp.producto || ''),
  m2: parseFloat(inp.m2) || 0,
  instalacion: inp.instalacion === true || inp.instalacion === 'true' || inp.instalacion === 'SI',
  total,
  estado: 'pendiente'
}};

try {{
  const resp = await fetch(SUPABASE_URL + '/rest/v1/cotizaciones', {{
    method: 'POST',
    headers: {{
      'Content-Type': 'application/json',
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Prefer': 'return=minimal'
    }},
    body: JSON.stringify(quote)
  }});

  const fmt = n => Number(n).toLocaleString('es-CL');
  return [{{
    json: {{
      numero,
      exito: resp.ok,
      mensaje: resp.ok
        ? '✅ Cotización N° ' + numero + ' generada.\\n👤 ' + quote.nombre + ' — ' + quote.rut + '\\n📍 ' + quote.direccion + '\\n🌿 ' + quote.producto + ' — ' + quote.m2 + ' m²\\n💰 Total: $' + fmt(total) + '\\n\\nEscribe PAGAR para continuar con el pago.'
        : 'Error guardando cotización: ' + resp.status
    }}
  }}];
}} catch(e) {{
  return [{{ json: {{ error: String(e.message), numero }} }}];
}}
""".strip()

# ─── TOOL: generar_pago ─────────────────────────────────────────────────────
TOOL_PAGO = f"""
const inp = $input.first().json;
const SUPABASE_URL = '{SUPABASE_URL}';
const SUPABASE_KEY = '{SUPABASE_KEY}';

// Buscar cotización en Supabase
let cotizacion = null;
try {{
  const r = await fetch(SUPABASE_URL + '/rest/v1/cotizaciones?numero=eq.' + encodeURIComponent(inp.numero_cotizacion || '') + '&select=*', {{
    headers: {{ 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY }}
  }});
  const data = await r.json();
  cotizacion = Array.isArray(data) && data.length > 0 ? data[0] : null;
}} catch(e) {{}}

if (!cotizacion) {{
  return [{{ json: {{ error: 'No se encontró la cotización ' + inp.numero_cotizacion }} }}];
}}

// Llamar MercadoPago
const MP_TOKEN = 'TEST-...';  // Reemplazar con token real
const mpBody = {{
  items: [{{
    title: 'Césped Sintético ARM — ' + cotizacion.producto,
    quantity: 1,
    currency_id: 'CLP',
    unit_price: cotizacion.total
  }}],
  back_urls: {{ success: 'https://tratohecho.cl/gracias', failure: 'https://tratohecho.cl', pending: 'https://tratohecho.cl' }},
  auto_return: 'approved',
  external_reference: cotizacion.numero
}};

try {{
  const mpResp = await fetch('https://api.mercadopago.com/checkout/preferences', {{
    method: 'POST',
    headers: {{
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + MP_TOKEN
    }},
    body: JSON.stringify(mpBody)
  }});
  const mpData = await mpResp.json();
  const link = mpData.init_point || mpData.sandbox_init_point || '';
  return [{{ json: {{ link, numero: cotizacion.numero, mensaje: link ? '💳 Link de pago: ' + link : 'Error generando link de pago' }} }}];
}} catch(e) {{
  return [{{ json: {{ error: String(e.message) }} }}];
}}
""".strip()

# ─── NODE IDs ────────────────────────────────────────────────────────────────
ID = {k: str(uuid.uuid4()) for k in ['webhook','extraer','agent','llm','memory','calc','guardar','pago','responder']}
WH_UUID = str(uuid.uuid4())

# ─── NODES ───────────────────────────────────────────────────────────────────
nodes = [
  {
    "id": ID['webhook'],
    "name": "Webhook Chat",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [-400, 300],
    "webhookId": WH_UUID,
    "parameters": {
      "httpMethod": "POST",
      "path": "chat-v2",
      "responseMode": "responseNode",
      "options": {"allowedOrigins": "*"}
    }
  },
  {
    "id": ID['extraer'],
    "name": "Extraer Input",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [-180, 300],
    "parameters": {
      "jsCode": (
        "const raw = $input.first().json;\n"
        "const body = raw.body || raw;\n"
        "const sessionId = String(body.sessionId || body.uuid || '').trim()\n"
        "  || 'auto_' + Date.now() + '_' + Math.random().toString(36).substr(2,6);\n"
        "const chatInput = String(body.message || body.chatInput || '').trim();\n"
        "if (!chatInput) throw new Error('message es requerido');\n"
        "return [{ json: { sessionId, chatInput } }];"
      )
    }
  },
  {
    "id": ID['agent'],
    "name": "AI Agent",
    "type": "@n8n/n8n-nodes-langchain.agent",
    "typeVersion": 1.7,
    "position": [80, 300],
    "parameters": {
      "agent": "conversationalAgent",
      "promptType": "define",
      "text": "={{ $json.chatInput }}",
      "sessionIdType": "customKey",
      "sessionKey": "={{ $json.sessionId }}",
      "options": {
        "systemMessage": SYSTEM_PROMPT
      }
    }
  },
  {
    "id": ID['llm'],
    "name": "Anthropic Claude Sonnet",
    "type": "@n8n/n8n-nodes-langchain.lmChatAnthropic",
    "typeVersion": 1.3,
    "position": [-60, 520],
    "parameters": {
      "model": "claude-sonnet-4-5",
      "options": {
        "maxTokens": 1024
      }
    },
    "credentials": {
      "anthropicApi": {"id": ANTHROPIC_CRED_ID, "name": "Anthropic account"}
    }
  },
  {
    "id": ID['memory'],
    "name": "Window Buffer Memory",
    "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
    "typeVersion": 1.3,
    "position": [80, 520],
    "parameters": {
      "sessionIdType": "customKey",
      "sessionKey": "={{ $('Extraer Input').first().json.sessionId }}",
      "contextWindowLength": 20
    }
  },
  {
    "id": ID['calc'],
    "name": "Tool calcular_precio",
    "type": "@n8n/n8n-nodes-langchain.toolCode",
    "typeVersion": 1.1,
    "position": [220, 520],
    "parameters": {
      "name": "calcular_precio",
      "description": "Calcula el precio total del pasto sintético. Úsala cuando el cliente haya elegido un producto y tenga m² definidos. Devuelve desglose detallado con subtotales y total.",
      "workflowInputs": {
        "values": [
          {"name": "producto", "type": "string"},
          {"name": "m2", "type": "number"},
          {"name": "con_instalacion", "type": "boolean"}
        ]
      },
      "jsCode": TOOL_CALCULAR
    }
  },
  {
    "id": ID['guardar'],
    "name": "Tool guardar_cotizacion",
    "type": "@n8n/n8n-nodes-langchain.toolCode",
    "typeVersion": 1.1,
    "position": [360, 520],
    "parameters": {
      "name": "guardar_cotizacion",
      "description": "Guarda la cotización en la base de datos y retorna el número de cotización. Úsala cuando tengas nombre, RUT, dirección, producto, m² y total del cliente.",
      "workflowInputs": {
        "values": [
          {"name": "session_id", "type": "string"},
          {"name": "nombre", "type": "string"},
          {"name": "rut", "type": "string"},
          {"name": "direccion", "type": "string"},
          {"name": "producto", "type": "string"},
          {"name": "m2", "type": "number"},
          {"name": "instalacion", "type": "boolean"},
          {"name": "total", "type": "number"}
        ]
      },
      "jsCode": TOOL_GUARDAR
    }
  },
  {
    "id": ID['pago'],
    "name": "Tool generar_pago",
    "type": "@n8n/n8n-nodes-langchain.toolCode",
    "typeVersion": 1.1,
    "position": [500, 520],
    "parameters": {
      "name": "generar_pago",
      "description": "Genera un link de pago MercadoPago para una cotización existente. Requiere el número de cotización.",
      "workflowInputs": {
        "values": [
          {"name": "numero_cotizacion", "type": "string"}
        ]
      },
      "jsCode": TOOL_PAGO
    }
  },
  {
    "id": ID['responder'],
    "name": "Responder Webhook",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [340, 300],
    "parameters": {
      "respondWith": "json",
      "responseBody": "={{ JSON.stringify({ message: $json.output || '', action: 'CHAT', quote: null, paymentLink: null }) }}"
    }
  }
]

# ─── CONNECTIONS ─────────────────────────────────────────────────────────────
connections = {
  "Webhook Chat": {
    "main": [[{"node": "Extraer Input", "type": "main", "index": 0}]]
  },
  "Extraer Input": {
    "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
  },
  "AI Agent": {
    "main": [[{"node": "Responder Webhook", "type": "main", "index": 0}]]
  },
  "Anthropic Claude Sonnet": {
    "ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]
  },
  "Window Buffer Memory": {
    "ai_memory": [[{"node": "AI Agent", "type": "ai_memory", "index": 0}]]
  },
  "Tool calcular_precio": {
    "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
  },
  "Tool guardar_cotizacion": {
    "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
  },
  "Tool generar_pago": {
    "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
  }
}

workflow = {
  "name": "Trato Hecho - AI Agent v2",
  "nodes": nodes,
  "connections": connections,
  "settings": {"executionOrder": "v1"}
}

# ─── DEPLOY ───────────────────────────────────────────────────────────────────
print("Creando workflow AI Agent v2...")
result = n8n('/workflows', 'POST', workflow)
if not result:
    print("ERROR creando workflow")
    exit(1)

wf_id = result['id']
print(f"Workflow creado. ID: {wf_id}")
print(f"Nodos: {[n['name'] for n in result['nodes']]}")

# Activar
import time
time.sleep(1)
activated = n8n(f'/workflows/{wf_id}/activate', 'POST', {})
if activated:
    print(f"Activado. active={activated.get('active')}")

time.sleep(3)

# Test
print("\nProbando webhook /webhook/chat-v2 ...")
import urllib.error
body = json.dumps({'message': 'hola', 'sessionId': 'test-v2-agent'}).encode()
req = urllib.request.Request('http://localhost:5678/webhook/chat-v2', data=body, method='POST')
req.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req, timeout=40) as r:
        resp = json.loads(r.read())
        print("RESPUESTA:", resp.get('message', '')[:200])
except urllib.error.HTTPError as e:
    print("HTTP error:", e.code, e.read().decode()[:300])
except Exception as ex:
    print("Error:", ex)

print(f"\nWorkflow ID: {wf_id}")
print(f"URL produccion: http://localhost:5678/webhook/chat-v2")
print(f"Para actualizar chatbot.js: cambia /webhook/chat por /webhook/chat-v2")
