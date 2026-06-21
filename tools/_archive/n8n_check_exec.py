import os
import urllib.request, json

KEY = os.environ.get('N8N_API_KEY', '')
WF = '4K4vFiRWRG63N92B'

req = urllib.request.Request('http://localhost:5678/api/v1/executions?workflowId=' + WF + '&limit=1')
req.add_header('X-N8N-API-KEY', KEY)
with urllib.request.urlopen(req) as r:
    execs = json.load(r)

last = execs['data'][0]
print('STATUS:', last['status'])
exec_id = str(last['id'])

req2 = urllib.request.Request('http://localhost:5678/api/v1/executions/' + exec_id + '?includeData=true')
req2.add_header('X-N8N-API-KEY', KEY)
with urllib.request.urlopen(req2) as r:
    ex = json.load(r)

rd = ex.get('data', {}).get('resultData', {})
err = rd.get('error', {})
if err:
    print('GLOBAL ERROR:', json.dumps(err, ensure_ascii=False)[:600])

run_data = rd.get('runData', {})
for node_name, node_runs in run_data.items():
    for run in node_runs:
        nerr = run.get('error', {})
        if nerr:
            print('NODE ERROR [' + node_name + ']:', json.dumps(nerr, ensure_ascii=False)[:400])
        out = run.get('data', {}).get('main', [[]])
        if out and out[0]:
            item = out[0][0].get('json', {})
            print('  OUTPUT [' + node_name + ']:', str(item)[:200])
