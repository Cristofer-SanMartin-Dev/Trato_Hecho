import os
import urllib.request, json

KEY = os.environ.get('N8N_API_KEY', '')
API = 'http://localhost:5678/api/v1'

def get(path):
    req = urllib.request.Request(API + path, headers={'X-N8N-API-KEY': KEY})
    return json.loads(urllib.request.urlopen(req).read())

execs = get('/executions?workflowId=4K4vFiRWRG63N92B&limit=3')['data']
# Mostrar la ejecución más reciente con detalle completo
ex = execs[0]
print(f'--- Exec {ex["id"]} | {ex["status"]}')
data = get(f'/executions/{ex["id"]}')
rd = data.get('data',{}).get('resultData',{}).get('runData',{})
print('Nodos ejecutados:', list(rd.keys()))

for k,v in rd.items():
    print(f'\n=== NODE: {k} ===')
    try:
        # Intentar obtener output principal
        main_data = v[0].get('data',{}).get('main',[[]])
        for i, arr in enumerate(main_data):
            if arr:
                for item in arr[:1]:
                    txt = json.dumps(item.get('json',{}), ensure_ascii=False)
                    print(f'  main[{i}][0].json: {txt[:400]}')
    except Exception as e:
        print('  err:', e)
    # Ver error del nodo
    if v[0].get('error'):
        print('  NODE ERROR:', str(v[0]['error'])[:300])
