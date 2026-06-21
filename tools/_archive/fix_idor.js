/**
 * fix_idor.js — TAREA 3
 * Cierra IDOR en Buscar en Supabase: agrega filtro session_id a la consulta.
 */
const fs = require('fs');
const WF_PATH = 'n8n/Trato Hecho - AI Agent v2.json';
const wf = JSON.parse(fs.readFileSync(WF_PATH, 'utf8'));

const NEW_BUSCAR_SUPABASE = [
  "const agentOutput = $input.first().json;",
  "const message = String(agentOutput.output || '');",
  "",
  "const buscarMatch = message.match(/\\[BUSCAR_COT:numero=([^\\s\\]]+)\\]/i);",
  "const pagoMatch   = message.match(/\\[PAGAR_MP:numero=([^,\\s\\]]+)/i);",
  "",
  "if (!buscarMatch && !pagoMatch) {",
  "  return [{ json: agentOutput }];",
  "}",
  "",
  "let numero = (buscarMatch ? buscarMatch[1] : pagoMatch[1]).trim().replace(/['\"]/g, '').toUpperCase();",
  "",
  "const SUPABASE_URL = '$env.SUPABASE_URL';",
  "const SUPABASE_KEY = '$env.SUPABASE_KEY';",
  "const fmt = n => Number(n || 0).toLocaleString('es-CL');",
  "",
  "// Obtener sessionId para el filtro anti-IDOR",
  "let sessionId = '';",
  "try { sessionId = $('Extraer Input').first().json.sessionId || ''; } catch(e) {}",
  "",
  "let newOutput;",
  "try {",
  "  const buscarEnSupabase = async (num) => {",
  "    // IDOR fix: filtrar siempre por session_id del usuario actual",
  "    let url = SUPABASE_URL + '/rest/v1/cotizaciones?numero=eq.' + encodeURIComponent(num) + '&limit=1';",
  "    if (sessionId) url += '&session_id=eq.' + encodeURIComponent(sessionId);",
  "    return await this.helpers.httpRequest({",
  "      method: 'GET',",
  "      url,",
  "      headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY }",
  "    });",
  "  };",
  "",
  "  let resp = await buscarEnSupabase(numero);",
  "  let data = Array.isArray(resp) ? resp : JSON.parse(String(resp));",
  "",
  "  // Intentar variante COT/C0T si no se encontró",
  "  if (data.length === 0) {",
  "    const alt = numero.includes('COT') ? numero.replace('COT', 'C0T') : numero.replace('C0T', 'COT');",
  "    resp = await buscarEnSupabase(alt);",
  "    data = Array.isArray(resp) ? resp : JSON.parse(String(resp));",
  "  }",
  "",
  "  const row = data.length > 0 ? data[0] : null;",
  "",
  "  // Mensaje genérico si no existe O pertenece a otra sesión (no revelar cuale es cuál)",
  "  if (!row) {",
  "    newOutput = 'No encontré esa cotización en tu historial. Verifica el número en tu correo o genera una nueva.';",
  "    return [{ json: { ...agentOutput, output: newOutput } }];",
  "  }",
  "",
  "  if (row.estado === 'C') {",
  "    newOutput = '\\u26a0\\ufe0f La cotización N° ' + row.numero + ' ya figura como PAGADA. No es posible volver a pagarla.';",
  "    return [{ json: { ...agentOutput, output: newOutput } }];",
  "  }",
  "",
  "  const created = new Date(row.created_at);",
  "  const diffDays = Math.ceil((new Date() - created) / (1000 * 60 * 60 * 24));",
  "  if (row.estado === 'V' || diffDays > 10) {",
  "    newOutput = '\\u26a0\\ufe0f La cotización N° ' + row.numero + ' ya no está vigente (más de 10 días). Por favor, genera una nueva.';",
  "    return [{ json: { ...agentOutput, output: newOutput } }];",
  "  }",
  "",
  "  // Si es marker de pago, inyectamos la data y seguimos al nodo Generar Pago MP",
  "  if (pagoMatch) {",
  "    return [{ json: { ...agentOutput, _quote_data: row } }];",
  "  }",
  "",
  "  // Si es marker de búsqueda, formateamos el resumen",
  "  newOutput = '\\ud83d\\udcc4 Cotización N° ' + row.numero + '\\n' +",
  "    '\\ud83d\\udc64 ' + (row.nombre || '') + ' \\u2014 ' + (row.rut || '') + '\\n' +",
  "    '\\ud83d\\udce7 ' + (row.email || '') + (row.telefono ? '\\n\\ud83d\\udcde ' + row.telefono : '') + '\\n' +",
  "    '\\ud83d\\udccd ' + (row.direccion || '') + '\\n' +",
  "    '\\ud83c\\udf3f ' + (row.producto || '') + ' \\u2014 ' + (row.m2 || 0) + ' m\\u00b2\\n' +",
  "    '\\ud83d\\udcb0 Total: $' + fmt(row.total) + '\\n' +",
  "    '\\ud83d\\udcc5 Fecha: ' + new Date(row.created_at).toLocaleDateString('es-CL') + '\\n\\n' +",
  "    (row.total > 0 ? 'Escribe PAGAR para continuar con el pago.' : 'Un asesor te contactará con el precio final.');",
  "",
  "  return [{ json: { ...agentOutput, output: newOutput, _quote_data: row } }];",
  "",
  "} catch(e) {",
  "  console.error('Supabase error:', e.message);",
  "  return [{ json: agentOutput }];",
  "}"
].join('\n');

let changed = 0;
wf.nodes.forEach(n => {
  if (n.name === 'Buscar en Supabase') {
    n.parameters.jsCode = NEW_BUSCAR_SUPABASE;
    console.log('OK Buscar en Supabase actualizado (filtro session_id anti-IDOR)');
    changed++;
  }
});

fs.writeFileSync(WF_PATH, JSON.stringify(wf, null, 2), 'utf8');
console.log(changed + ' nodos actualizados.');
