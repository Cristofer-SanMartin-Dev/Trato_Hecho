import os
import urllib.request, json

KEY = os.environ.get('N8N_API_KEY', '')
WF_ID = "4K4vFiRWRG63N92B"

# --- Obtener workflow actual ---
req = urllib.request.Request(f"http://localhost:5678/api/v1/workflows/{WF_ID}")
req.add_header("X-N8N-API-KEY", KEY)
with urllib.request.urlopen(req) as r:
    wf = json.load(r)

agent = next(n for n in wf["nodes"] if n["name"] == "AI Agent")
old_prompt = agent["parameters"]["options"]["systemMessage"]

# --- Nuevas reglas a agregar ---
new_rules = (
    "\n\n== DESCUENTO POR VOLUMEN ==\n"
    "Si el total calculado supera $1.000.000 Y el cliente expresa que el precio es alto "
    "(frases como: esta muy caro, tienes rebaja, me puedes hacer un descuento, es mucho, "
    "no tengo tanto, que descuento me das, me puedes descontar, o similares):\n"
    "- Aplica un 10% de descuento sobre el total.\n"
    "- Muestra el precio original, el descuento aplicado ($XXX) y el nuevo total.\n"
    "- Di: \"Por tratarse de un proyecto de gran volumen, te aplicamos un 10% de descuento especial.\"\n"
    "- Si el cliente luego escribe COTIZAR, usa el total con descuento como valor final.\n"
    "- Este descuento solo se aplica UNA vez por conversacion.\n"
    "\n"
    "== CONTACTO CON ASESOR ==\n"
    "Si el cliente dice que no quiere continuar por ahora, que prefiere hablar con una persona, "
    "que quiere contactar a alguien, o que quiere hablar con un asesor (frases como: prefiero "
    "hablar con alguien, quiero hablar con una persona, no me interesa por ahora, lo pensare, "
    "me comunico despues, llamame, quiero que me llamen, o similares), responde EXACTAMENTE asi, "
    "sin agregar texto antes ni despues:\n"
    "\"Claro, puedes contactar directamente con uno de nuestros asesores: [WZP:+56975834364]\""
)

agent["parameters"]["options"]["systemMessage"] = old_prompt + new_rules

payload = json.dumps({
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": {
        "executionOrder": "v1",
        "callerPolicy": "workflowsFromSameOwner",
        "saveDataSuccessExecution": "all",
        "saveDataErrorExecution": "all",
        "saveManualExecutions": True
    }
}).encode("utf-8")

put_req = urllib.request.Request(
    f"http://localhost:5678/api/v1/workflows/{WF_ID}",
    data=payload,
    method="PUT"
)
put_req.add_header("X-N8N-API-KEY", KEY)
put_req.add_header("Content-Type", "application/json")

try:
    with urllib.request.urlopen(put_req) as r:
        resp = json.load(r)
        updated_agent = next(n for n in resp["nodes"] if n["name"] == "AI Agent")
        new_len = len(updated_agent["parameters"]["options"]["systemMessage"])
        print(f"OK - System prompt actualizado. Nuevo largo: {new_len} chars")
        print("Ultimas 150 chars:", updated_agent["parameters"]["options"]["systemMessage"][-150:])
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP {e.code}: {body[:500]}")
