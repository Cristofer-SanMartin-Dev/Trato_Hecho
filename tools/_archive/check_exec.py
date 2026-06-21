import os
import urllib.request, json

key = os.environ.get('N8N_API_KEY', '')

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
