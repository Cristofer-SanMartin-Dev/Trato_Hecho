import requests, json

key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"
headers = {"X-N8N-API-KEY": key, "Content-Type": "application/json"}

r = requests.get("http://localhost:5678/api/v1/workflows/4K4vFiRWRG63N92B", headers=headers)
data = r.json()

NUEVO_SALUDO = (
    "- Cuando el primer mensaje del usuario sea solo un saludo "
    "(hola, buenas, hey, buenos dias, buenas tardes, etc.), responde EXACTAMENTE: "
    '"Hola, soy Queno, tu asistente de ventas para pasto sintetico. '
    "Dime en que puedo ayudarte hoy. Si tienes una cotizacion anterior, ingresa el numero y la buscamos juntos. "
    "Si no la recuerdas, la puedes buscar en tu correo. "
    'Si es una cotizacion o venta nueva, solo hazme saber y avanzamos juntos."'
)

VIEJO = '- NUNCA saludar con "Hola" si ya hay historial anterior.'
NUEVO = NUEVO_SALUDO + "\n" + VIEJO

for node in data["nodes"]:
    if node.get("name") == "AI Agent":
        sp = node["parameters"]["options"]["systemMessage"]
        if VIEJO in sp:
            sp_new = sp.replace(VIEJO, NUEVO, 1)
            node["parameters"]["options"]["systemMessage"] = sp_new
            print("OK: regla de saludo agregada")
        else:
            print("ERROR: texto no encontrado en system prompt")
            print("Buscando:", repr(VIEJO[:60]))
        break

ALLOWED_SETTINGS = {
    "executionOrder", "saveDataSuccessExecution", "saveDataErrorExecution",
    "saveManualExecutions", "timezone", "errorWorkflow", "saveExecutionProgress"
}
payload = {
    "name": data["name"],
    "nodes": data["nodes"],
    "connections": data["connections"],
    "settings": {k: v for k, v in data.get("settings", {}).items() if k in ALLOWED_SETTINGS},
    "staticData": data.get("staticData", None),
}
r2 = requests.put("http://localhost:5678/api/v1/workflows/4K4vFiRWRG63N92B", headers=headers, json=payload)
print("Status:", r2.status_code)
if r2.status_code not in (200, 201):
    print(r2.text[:400])
else:
    print("Workflow guardado correctamente")
