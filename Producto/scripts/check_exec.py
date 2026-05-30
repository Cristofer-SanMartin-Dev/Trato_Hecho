import urllib.request, json

key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw'

req = urllib.request.Request('http://localhost:5678/api/v1/executions/129?includeData=true', method='GET')
req.add_header('X-N8N-API-KEY', key)
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())

print('STATUS:', data.get('status'))
last_node = data.get('data', {}).get('resultData', {}).get('lastNodeExecuted')
print('LAST NODE:', last_node)

top_err = data.get('data', {}).get('resultData', {}).get('error')
if top_err:
    print('TOP ERROR:', json.dumps(top_err, indent=2)[:800])

run_data = data.get('data', {}).get('resultData', {}).get('runData', {})
for node_name, runs in run_data.items():
    for run in runs:
        status = run.get('executionStatus', '?')
        print('NODE:', node_name, '| status:', status)
        if run.get('error'):
            print('  ERROR:', str(run['error'])[:400])
