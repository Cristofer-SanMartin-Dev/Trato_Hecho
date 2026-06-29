import os
import urllib.request, json

key = os.environ.get('N8N_API_KEY', '')

req = urllib.request.Request('http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij', method='GET')
req.add_header('X-N8N-API-KEY', key)
with urllib.request.urlopen(req) as r:
    wf = json.load(r)

changed = []
for n in wf['nodes']:
    name = n['name']

    # Fix 1: Guardar Historial - continuar aunque falle RLS
    if name == 'Guardar Historial Supabase':
        n['onError'] = 'continueRegularOutput'
        n['alwaysOutputData'] = True
        changed.append(name + ':continueOnError')

    # Fix 2: Switch Accion - leer action de Parsear Respuesta Claude (no de $json que llega vacio)
    if name == 'Switch Acción':
        rules = n.get('parameters', {}).get('rules', {}).get('values', [])
        for rule in rules:
            conds = rule.get('conditions', {}).get('conditions', [])
            for c in conds:
                if '$json.action' in c.get('leftValue', ''):
                    c['leftValue'] = "={{ $('Parsear Respuesta Claude').first().json.action }}"
                    changed.append(name + ':action-ref')

    # Fix 3: Respuesta Simple - leer cleanText de Parsear Respuesta Claude
    if name == 'Respuesta Simple':
        new_code = (
            "// Respuesta simple (sin accion especial)\n"
            "const parseData = $('Parsear Respuesta Claude').first().json;\n"
            "\n"
            "return [{\n"
            "  json: {\n"
            "    message: parseData.cleanText || parseData.rawText || '',\n"
            "    quote: parseData.existingQuote || null,\n"
            "    paymentLink: null\n"
            "  }\n"
            "}];"
        )
        n['parameters']['jsCode'] = new_code
        changed.append(name + ':jsCode')

print('Cambios a aplicar:', changed)

# Deactivate
r0 = urllib.request.Request('http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij/deactivate', method='POST')
r0.add_header('X-N8N-API-KEY', key)
r0.add_header('Content-Type', 'application/json')
urllib.request.urlopen(r0).read()
print('Desactivado.')

# PUT actualizar workflow — solo campos permitidos por la API
raw_settings = wf.get('settings', {})
allowed_settings_keys = {
    'executionOrder', 'saveManualExecutions', 'callerPolicy',
    'errorWorkflow', 'timezone', 'saveDataSuccessExecution',
    'saveDataErrorExecution', 'executionTimeout', 'maxExecutionTimeout'
}
clean_settings = {k: v for k, v in raw_settings.items() if k in allowed_settings_keys}

body = json.dumps({
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': clean_settings,
    'staticData': wf.get('staticData')
}).encode('utf-8')

r2 = urllib.request.Request('http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij', data=body, method='PUT')
r2.add_header('X-N8N-API-KEY', key)
r2.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(r2) as resp:
        result = json.load(resp)
        print('Desplegado. Active:', result.get('active'))
except urllib.error.HTTPError as e:
    print('PUT Error', e.code, e.reason)
    print(e.read().decode()[:500])

# Reactivate
r3 = urllib.request.Request('http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij/activate', method='POST')
r3.add_header('X-N8N-API-KEY', key)
r3.add_header('Content-Type', 'application/json')
urllib.request.urlopen(r3).read()
print('Reactivado OK.')
