import os
import urllib.request, json

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
10. Dirección obtenida → llama guardar_cotizacion con todos los datos → copia y pega EXACTAMENTE el campo "mensaje" que retorna la herramienta, sin agregar ni quitar nada, sin reformatear

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
    # n8n PUT requires only these fields
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

wf = api_get(f'workflows/{WF_ID}')
print('Got workflow:', wf['name'])

# Update AI Agent node systemMessage
updated = False
for node in wf['nodes']:
    if node.get('type') == '@n8n/n8n-nodes-langchain.agent':
        node['parameters']['options']['systemMessage'] = NEW_SYSTEM_PROMPT
        updated = True
        print('Updated systemMessage in AI Agent node')
        break

if not updated:
    print('ERROR: AI Agent node not found')
    exit(1)

# PUT only the required fields
result = api_put(WF_ID, wf)
print('PATCH result: nodes=', len(result.get('nodes', [])))

# Re-activate
req_act = urllib.request.Request(
    f'{API}/workflows/{WF_ID}/activate', method='POST',
    headers={'X-N8N-API-KEY': KEY, 'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req_act) as r:
    act = json.loads(r.read())
print('Active:', act.get('active'))

# Quick test
import urllib.request as ur
import time
time.sleep(1)
b = json.dumps({'message': 'hola', 'sessionId': 'prompt-update-test'}).encode()
req2 = ur.Request('http://localhost:5678/webhook/chat-v2', data=b, method='POST',
                   headers={'Content-Type': 'application/json'})
with ur.urlopen(req2, timeout=40) as r:
    print('TEST:', json.loads(r.read()).get('message', '')[:100])
