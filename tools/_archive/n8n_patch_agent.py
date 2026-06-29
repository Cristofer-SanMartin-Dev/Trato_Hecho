"""
patch_agent.py
Parchea el workflow JSON de n8n con las correcciones al agente:
  1. Reemplaza el código del nodo "Construir Prompt Claude" con instruccionInmediata
  2. Corrige "Preparar Historial" para guardar rawText en vez de cleanText
"""
import json, re, sys
from pathlib import Path

WORKFLOW_FILE = Path(__file__).parent / "Trato Hecho - Chat Agent (2).json"
CODE_FILE     = Path(__file__).parent / "construir_code.txt"

# ── Código nuevo para "Construir Prompt Claude" ────────────────────────────────
NEW_CONSTRUIR = CODE_FILE.read_text(encoding="utf-8")

# ── Código nuevo para "Preparar Historial" ────────────────────────────────────
NEW_PREPARAR = r"""const extract = $('Extraer Input').first()?.json || {};
const parse   = $('Parsear Respuesta Claude').first()?.json || {};

const uuid         = extract.uuid || 'anonimo';
const userMsg      = extract.message || '';
// Guardar rawText para mantener las etiquetas [COTIZAR:] en el historial
const assistantMsg = parse.rawText || parse.cleanText || parse.fullResponse || '';

// Leer historial previo desde Supabase
let history = [];
try {
  const raw = $('GET Historial Supabase').first()?.json;
  if (Array.isArray(raw) && raw.length > 0 && Array.isArray(raw[0].messages)) {
    history = raw[0].messages;
  } else if (raw && Array.isArray(raw.messages)) {
    history = raw.messages;
  }
} catch(e) {}

// Fallback bodyHistory del frontend
if (!Array.isArray(history) || history.length === 0) {
  try {
    const bh = extract.bodyHistory;
    if (Array.isArray(bh)) history = bh;
  } catch(e) {}
}

if (!Array.isArray(history)) history = [];
history = history.filter(m => m && m.content);

// Agregar el turno actual
history.push({ role: 'user', content: userMsg });
history.push({ role: 'assistant', content: assistantMsg });

// Máximo 40 mensajes (20 turnos)
history = history.slice(-40);

return [{ json: { uuid, history, message: userMsg, assistantMsg } }];"""

def patch_workflow():
    if not WORKFLOW_FILE.exists():
        print(f"ERROR: No se encontró el archivo '{WORKFLOW_FILE}'")
        sys.exit(1)

    with open(WORKFLOW_FILE, encoding="utf-8") as f:
        workflow = json.load(f)

    patched_construir = False
    patched_preparar  = False

    for node in workflow.get("nodes", []):
        name = node.get("name", "")
        params = node.get("parameters", {})

        if name == "Construir Prompt Claude" and "jsCode" in params:
            params["jsCode"] = NEW_CONSTRUIR
            patched_construir = True
            print("[OK] Nodo 'Construir Prompt Claude' actualizado")

        elif name == "Preparar Historial" and "jsCode" in params:
            params["jsCode"] = NEW_PREPARAR
            patched_preparar = True
            print("[OK] Nodo 'Preparar Historial' actualizado")

    if not patched_construir:
        print("[WARN] No se encontro el nodo 'Construir Prompt Claude'")
    if not patched_preparar:
        print("[WARN] No se encontro el nodo 'Preparar Historial'")

    with open(WORKFLOW_FILE, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    print(f"\nWorkflow guardado en: {WORKFLOW_FILE}")
    print("Listo. Reimporta el archivo en n8n: Workflows → Import from File")

if __name__ == "__main__":
    patch_workflow()
