/**
 * fix_session_id.js — TAREA 6
 * Reemplaza Math.random() en Extraer Input del workflow por crypto.randomUUID().
 */
const fs = require('fs');
const WF_PATH = 'n8n/Trato Hecho - AI Agent v2.json';
const wf = JSON.parse(fs.readFileSync(WF_PATH, 'utf8'));

const NEW_EXTRAER_INPUT = [
  "const raw = $input.first().json;",
  "const body = raw.body || raw;",
  "const sessionId = String(body.sessionId || body.uuid || '').trim()",
  "  || 'auto_' + Date.now() + '_' + require('crypto').randomUUID();",
  "const chatInput = String(body.message || body.chatInput || '').trim();",
  "if (!chatInput) throw new Error('message es requerido');",
  "return [{ json: { sessionId, chatInput } }];"
].join('\n');

let changed = 0;
wf.nodes.forEach(n => {
  if (n.name === 'Extraer Input') {
    const old = n.parameters.jsCode || '';
    if (old.includes('Math.random()')) {
      n.parameters.jsCode = NEW_EXTRAER_INPUT;
      console.log('OK Extraer Input actualizado (crypto.randomUUID)');
      changed++;
    }
  }
});

fs.writeFileSync(WF_PATH, JSON.stringify(wf, null, 2), 'utf8');
console.log(changed + ' nodos actualizados.');
