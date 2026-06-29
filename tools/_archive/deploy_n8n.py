import os
import json
import urllib.request

KEY = os.environ.get('N8N_API_KEY', '')
WORKFLOW_ID = "CjS3Gm0863S4j9Ij"
WF_PATH = r"n8n\Trato Hecho - Chat Agent (2).json"

with open(WF_PATH, "r", encoding="utf-8") as f:
    wf = json.load(f)

payload = json.dumps({
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": {"executionOrder": "v1"}
}).encode("utf-8")

req = urllib.request.Request(
    f"http://localhost:5678/api/v1/workflows/{WORKFLOW_ID}",
    data=payload,
    method="PUT"
)
req.add_header("X-N8N-API-KEY", KEY)
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req) as resp:
    r = json.loads(resp.read())
    print(f"Desplegado: {r['name']} - updatedAt: {r['updatedAt']}")
