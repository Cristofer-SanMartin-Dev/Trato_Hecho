import urllib.request, json

KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'
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
