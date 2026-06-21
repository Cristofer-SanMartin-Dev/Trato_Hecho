import os
import urllib.request, json, re

API = 'http://localhost:5678/api/v1'
KEY = os.environ.get('N8N_API_KEY', '')

req = urllib.request.Request(f'{API}/executions/202', headers={'X-N8N-API-KEY': KEY})
with urllib.request.urlopen(req) as r:
    exec_data = json.loads(r.read())

print('status:', exec_data.get('status'))

# Save full data
with open('n8n/exec202.json', 'w', encoding='utf-8') as f:
    json.dump(exec_data, f, indent=2, ensure_ascii=False)
print('Saved to n8n/exec202.json')

# Search for error messages
txt = json.dumps(exec_data, ensure_ascii=False)
for m in re.finditer(r'"(?:message|description|error)"\s*:\s*"([^"]{10,}?)"', txt):
    print(' -', m.group(1)[:200])
