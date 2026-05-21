import json
import urllib.request

KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"
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
