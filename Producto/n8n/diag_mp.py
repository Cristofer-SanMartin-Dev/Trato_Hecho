import urllib.request, json

KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'

# 1. Últimas ejecuciones
req = urllib.request.Request(
    'http://localhost:5678/api/v1/executions?limit=5&workflowId=4K4vFiRWRG63N92B',
    headers={'X-N8N-API-KEY': KEY}
)
execs = json.loads(urllib.request.urlopen(req).read())
last_id = execs['data'][0]['id']
print('Última ejecución:', last_id, '| status:', execs['data'][0]['status'])

# 2. Detalle de esa ejecución
req2 = urllib.request.Request(
    f'http://localhost:5678/api/v1/executions/{last_id}',
    headers={'X-N8N-API-KEY': KEY}
)
detail = json.loads(urllib.request.urlopen(req2).read())
rd = detail.get('data', {}).get('resultData', {}).get('runData', {})

for node_name, node_runs in rd.items():
    run = node_runs[0] if node_runs else {}
    items = run.get('data', {}).get('main', [[]])[0] if run.get('data') else []
    if items:
        j = items[0].get('json', {})
        output = j.get('output', '') or j.get('message', '') or str(j)
        print(f'\n[{node_name}] → {str(output)[:250]}')
    else:
        err = run.get('error', {})
        if err:
            print(f'\n[{node_name}] ERROR → {str(err)[:200]}')
