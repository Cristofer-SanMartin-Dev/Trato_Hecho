import urllib.request, json

KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'
API = 'http://localhost:5678/api/v1'

def get(path):
    req = urllib.request.Request(API + path, headers={'X-N8N-API-KEY': KEY})
    return json.loads(urllib.request.urlopen(req).read())

execs = get('/executions?workflowId=4K4vFiRWRG63N92B&limit=5')['data']
print('Ultimas ejecuciones:')
for e in execs:
    print(f'  id: {e["id"]} | status: {e["status"]}')

# Inspeccionar la última con error
for ex in execs:
    if ex['status'] == 'error':
        print(f'\n=== Error en exec {ex["id"]} ===')
        data = get(f'/executions/{ex["id"]}')
        err = data.get('data', {}).get('resultData', {}).get('error', {})
        if err:
            print('Node:', err.get('node', {}).get('name', '?'))
            print('Msg:', err.get('message', '')[:500])
            print('Desc:', err.get('description', '')[:300])
        # También ver todos los nodos y sus errores
        rd = data.get('data', {}).get('resultData', {}).get('runData', {})
        print('Nodos ejecutados:', list(rd.keys()))
        for k, v in rd.items():
            node_err = v[0].get('error') if v else None
            if node_err:
                print(f'  ERROR en {k}:', str(node_err)[:300])
            else:
                try:
                    out = v[0].get('data', {}).get('main', [[]])[0]
                    if out:
                        txt = json.dumps(out[0].get('json', {}), ensure_ascii=False)
                        print(f'  {k}: {txt[:200]}')
                except:
                    pass
        break
