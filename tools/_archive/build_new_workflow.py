import os
"""
Reconstruye el workflow de n8n reemplazando Redis con Supabase
y simplificando la lógica (Claude maneja todo via prompt).
"""
import json
import uuid as umod

SB_URL = os.environ.get('SUPABASE_URL', '')
SB_KEY = os.environ.get('SUPABASE_KEY', '')
PATH = r"n8n\Trato Hecho - Chat Agent (2).json"

with open(PATH, encoding="utf-8") as f:
    wf = json.load(f)

nb = {n["name"]: n for n in wf["nodes"]}

# ── Posiciones de los nodos Redis (reutilizamos para los Supabase) ──────────
pos_hist_get   = nb["Obtener Historial Redis"]["position"]
pos_quote_get  = nb["Obtener Cotización Redis"]["position"]
pos_hist_save  = nb["Guardar Historial Redis"]["position"]
pos_quote_save = nb.get("Guardar Cotización Redis", {}).get("position", [pos_hist_save[0]+220, pos_hist_save[1]+200])

# ── 1. jsCode: Construir Prompt Claude (prompt-only, Claude hace todo) ──────
CONSTRUIR_CODE = r"""
const extract = $('Extraer Input').first().json;
const { uuid, message, bodyHistory } = extract;

// 1. HISTORIAL: Supabase → fallback frontend
let history = [];
try {
  const raw = $('GET Historial Supabase').first()?.json;
  // Supabase devuelve array: [{messages:[...]}, ...] o []
  if (Array.isArray(raw) && raw.length > 0 && Array.isArray(raw[0].messages)) {
    history = raw[0].messages;
  } else if (raw && Array.isArray(raw.messages)) {
    history = raw.messages;
  }
} catch(e) {}
if (!Array.isArray(history) || history.length === 0) {
  if (Array.isArray(bodyHistory) && bodyHistory.length > 0) history = bodyHistory;
}
history = history.filter(m => m && m.content);

// 2. COTIZACIÓN EXISTENTE desde Supabase
let quoteContext = '';
try {
  const raw = $('GET Cotización Supabase').first()?.json;
  const q = Array.isArray(raw) && raw.length > 0 ? raw[0]
            : (raw && raw.numero ? raw : null);
  if (q) {
    quoteContext = '\n\nCOTIZACIÓN EXISTENTE #' + q.numero
      + ': ' + q.producto
      + ', ' + q.m2 + ' m²'
      + ', instalacion=' + (q.instalacion ? 'SI' : 'NO')
      + ', total=$' + Number(q.total).toLocaleString('es-CL')
      + '. Estado: ' + q.estado + '.';
  }
} catch(e) {}

// 3. SYSTEM PROMPT COMPLETO
const systemPrompt = `Eres Queno, vendedor virtual de Césped Sintético ARM en Melipilla, Chile.
Tu objetivo es vender césped sintético, tomar medidas, calcular precios y generar cotizaciones formales.
${quoteContext}

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

SI HAY COTIZACIÓN EXISTENTE en el contexto:
- Muéstrale los datos al cliente
- Ofrece: '¿Quieres proceder al pago?'
- Para iniciar pago usa: [PAGAR: numero=X, monto=X]

REGLAS ESTRICTAS:
- Máximo 4 líneas por respuesta. Solo 1 pregunta por mensaje.
- NUNCA saludar con 'Hola' si ya hay historial de conversación.
- NUNCA reiniciar el flujo si ya hay producto o datos recopilados.
- NUNCA pedir datos ya entregados en el historial.
- NUNCA calcular precios para productos deportivos (precio a cotizar).
- NUNCA agregar texto antes o después de [COTIZAR:] o [PAGAR:] cuando corresponda.
- No interpretar RUT, teléfono o código postal como metros cuadrados.
- Si el número parece fuera de rango (<1 o >1000 m2), confirma antes de continuar.
- Si el cliente cambia de producto, confirma el cambio explícitamente.`;

// 4. MENSAJES para Claude
const messages = [
  ...history.map(m => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content })),
  { role: 'user', content: message }
];

// 5. Body para Claude API
const claudeBody = JSON.stringify({
  model: 'claude-sonnet-4-5',
  max_tokens: 1024,
  system: systemPrompt,
  messages
});

return [{ json: { uuid, message, claudeBody, historyLength: history.length } }];
""".strip()

# ── 2. jsCode: Preparar Historial (usa Supabase, no Redis) ──────────────────
PREPARAR_CODE = r"""
const extract = $('Extraer Input').first()?.json || {};
const parse   = $('Parsear Respuesta Claude').first()?.json || {};

const uuid         = extract.uuid || 'anonimo';
const userMsg      = extract.message || '';
const assistantMsg = parse.cleanText || parse.fullResponse || '';

// Leer historial previo desde Supabase
let history = [];
try {
  const raw = $('GET Historial Supabase').first()?.json;
  if (Array.isArray(raw) && raw.length > 0 && Array.isArray(raw[0].messages)) {
    history = raw[0].messages;
  } else if (raw && Array.isArray(raw.messages)) {
    history = raw.messages;
  }
} catch(e) {}

// Fallback bodyHistory del frontend
if (!Array.isArray(history) || history.length === 0) {
  try {
    const bh = extract.bodyHistory;
    if (Array.isArray(bh)) history = bh;
  } catch(e) {}
}

if (!Array.isArray(history)) history = [];
history = history.filter(m => m && m.content);

// Agregar el turno actual
history.push({ role: 'user', content: userMsg });
history.push({ role: 'assistant', content: assistantMsg });

// Máximo 40 mensajes (20 turnos)
history = history.slice(-40);

return [{ json: { uuid, history, message: userMsg, assistantMsg } }];
""".strip()

# ── 3. jsCode: Crear Cotización (sin Incrementar Contador) ──────────────────
CREAR_CODE = r"""
const parseData  = $('Parsear Respuesta Claude').first().json;
const actionData = parseData.actionData || {};
const uuid       = parseData.uuid || $('Extraer Input').first().json.uuid || 'sin-uuid';
const cleanText  = parseData.cleanText || '';

// Número de cotización: COT-AÑO-XXXXX (basado en timestamp)
const year   = new Date().getFullYear();
const seq    = String(Date.now()).slice(-5);
const numero = 'COT-' + year + '-' + seq;

const total      = Number(actionData.total) || 0;
const m2         = Number(actionData.m2) || 0;
const instalacion = (String(actionData.instalacion || '')).toUpperCase() === 'SI';

const quote = {
  numero,
  session_id:  uuid,
  nombre:      actionData.nombre    || '',
  rut:         actionData.rut       || '',
  direccion:   actionData.direccion || '',
  producto:    actionData.tipo      || '',
  m2,
  instalacion,
  total,
  estado: 'pendiente'
};

const totalStr = total > 0
  ? '$' + total.toLocaleString('es-CL')
  : 'a cotizar';

const message = '✅ Cotización generada!\n'
  + '📋 N° ' + numero + '\n'
  + '👤 ' + quote.nombre + ' — ' + quote.rut + '\n'
  + '📍 ' + quote.direccion + '\n'
  + '🌿 ' + quote.producto + ' — ' + m2 + ' m²\n'
  + (instalacion ? '🔧 Con instalación\n' : '')
  + '💰 Total: ' + totalStr + '\n\n'
  + 'Escribe PAGAR para continuar con el pago.';

return [{ json: { quote, message, uuid, cleanText } }];
""".strip()

# ── 4. Aplicar los nuevos jsCode a los nodos existentes ─────────────────────
for n in wf["nodes"]:
    if n["name"] == "Construir Prompt Claude":
        n["parameters"]["jsCode"] = CONSTRUIR_CODE
    elif n["name"] == "Preparar Historial":
        n["parameters"]["jsCode"] = PREPARAR_CODE
    elif n["name"] == "Crear Cotización":
        n["parameters"]["jsCode"] = CREAR_CODE

# ── 5. Eliminar nodos Redis ──────────────────────────────────────────────────
REMOVE = {
    "Obtener Historial Redis",
    "Obtener Cotización Redis",
    "Guardar Historial Redis",
    "Guardar Cotización Redis",
    "Incrementar Contador",
}
wf["nodes"] = [n for n in wf["nodes"] if n["name"] not in REMOVE]

# ── 6. Agregar nodos Supabase (HTTP Request) ─────────────────────────────────
def sb_headers(*extra):
    entries = [
        {"name": "apikey",        "value": SB_KEY},
        {"name": "Authorization", "value": "Bearer " + SB_KEY},
    ]
    entries.extend(extra)
    return {"parameters": entries}

get_hist_node = {
    "parameters": {
        "method": "GET",
        "url": "={{ '" + SB_URL + "/rest/v1/historial?session_id=eq.' + $json.uuid + '&select=messages' }}",
        "sendHeaders": True,
        "headerParameters": sb_headers(),
        "options": {}
    },
    "id": str(umod.uuid4()),
    "name": "GET Historial Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": pos_hist_get,
}

get_quote_node = {
    "parameters": {
        "method": "GET",
        "url": "={{ '" + SB_URL + "/rest/v1/cotizaciones?session_id=eq.' + $('Extraer Input').first().json.uuid + '&order=created_at.desc&limit=1&select=*' }}",
        "sendHeaders": True,
        "headerParameters": sb_headers(),
        "options": {}
    },
    "id": str(umod.uuid4()),
    "name": "GET Cotización Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": pos_quote_get,
}

save_hist_node = {
    "parameters": {
        "method": "POST",
        "url": SB_URL + "/rest/v1/historial",
        "sendHeaders": True,
        "headerParameters": sb_headers(
            {"name": "Content-Type", "value": "application/json"},
            {"name": "Prefer",       "value": "resolution=merge-duplicates"},
        ),
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ session_id: $json.uuid, messages: $json.history, updated_at: new Date().toISOString() }) }}",
        "options": {}
    },
    "id": str(umod.uuid4()),
    "name": "Guardar Historial Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": pos_hist_save,
}

save_quote_node = {
    "parameters": {
        "method": "POST",
        "url": SB_URL + "/rest/v1/cotizaciones",
        "sendHeaders": True,
        "headerParameters": sb_headers(
            {"name": "Content-Type", "value": "application/json"},
            {"name": "Prefer",       "value": "return=representation"},
        ),
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json.quote) }}",
        "options": {}
    },
    "id": str(umod.uuid4()),
    "name": "Guardar Cotización Supabase",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": pos_quote_save,
}

wf["nodes"].extend([get_hist_node, get_quote_node, save_hist_node, save_quote_node])

# ── 7. Reconstruir connections ───────────────────────────────────────────────
edges = [
    # Flujo principal
    ("Webhook Chat",            0, "Extraer Input"),
    ("Extraer Input",           0, "GET Historial Supabase"),
    ("GET Historial Supabase",  0, "GET Cotización Supabase"),
    ("GET Cotización Supabase", 0, "Construir Prompt Claude"),
    ("Construir Prompt Claude", 0, "Llamar Claude API"),
    ("Llamar Claude API",       0, "Parsear Respuesta Claude"),
    ("Parsear Respuesta Claude",0, "Preparar Historial"),
    ("Preparar Historial",      0, "Guardar Historial Supabase"),
    ("Guardar Historial Supabase", 0, "Switch Acción"),
    # Rama COTIZAR (branch 0)
    ("Switch Acción",           0, "Crear Cotización"),
    ("Crear Cotización",        0, "Guardar Cotización Supabase"),
    ("Guardar Cotización Supabase", 0, "Respuesta Cotización"),
    ("Respuesta Cotización",    0, "Telegram - MsgeCotiza"),
    ("Telegram - MsgeCotiza",   0, "MsjeCotiza"),
    ("MsjeCotiza",              0, "Responder Webhook (Cotizar)"),
    # Rama PAGAR (branch 1)
    ("Switch Acción",           1, "If"),
    ("If",                      0, "Llamar MercadoPago"),
    ("If",                      1, "Respuesta Sin Cotización1"),
    ("Llamar MercadoPago",      0, "Respuesta Pago"),
    ("Respuesta Pago",          0, "Send a text message1"),
    ("Send a text message1",    0, "MsjeVenta1"),
    ("MsjeVenta1",              0, "Responder Webhook (Pagar)"),
    ("Respuesta Sin Cotización1",0,"Responder Webhook (Sin Cotización)1"),
    # Rama CHAT (branch 2)
    ("Switch Acción",           2, "Respuesta Simple"),
    ("Respuesta Simple",        0, "Responder Webhook (Simple)"),
]

new_conns = {}
for src, branch, dst in edges:
    if src not in new_conns:
        new_conns[src] = {"main": []}
    while len(new_conns[src]["main"]) <= branch:
        new_conns[src]["main"].append([])
    new_conns[src]["main"][branch].append({"node": dst, "type": "main", "index": 0})

wf["connections"] = new_conns

# ── 8. Guardar ───────────────────────────────────────────────────────────────
with open(PATH, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print("Workflow reconstruido OK")
print("  Nodos totales:          ", len(wf["nodes"]))
print("  Nodos Redis eliminados: ", len(REMOVE))
print("  Nodos Supabase nuevos:  ", 4)
