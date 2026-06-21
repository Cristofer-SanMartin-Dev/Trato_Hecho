/**
 * fix_price_vuln.js — TAREA 2
 * Corrige manipulación de precio: el total siempre viene de Supabase, nunca del LLM.
 */
const fs = require('fs');
const WF_PATH = 'n8n/Trato Hecho - AI Agent v2.json';
const wf = JSON.parse(fs.readFileSync(WF_PATH, 'utf8'));

const NEW_TOOL_GENERAR_PAGO = [
  "let inp = {};",
  "try {",
  "  if (typeof query !== 'undefined' && query) {",
  "    inp = (typeof query === 'string') ? JSON.parse(query) : query;",
  "  } else {",
  "    const raw = $input.first().json;",
  "    const q = raw.query || raw;",
  "    inp = (typeof q === 'string') ? JSON.parse(q) : q;",
  "  }",
  "} catch(e) { inp = {}; }",
  "",
  "const numero = String(inp.numero_cotizacion || inp.numero || '').trim();",
  "",
  "if (!numero || !numero.match(/^C[O0]T-/i)) {",
  "  return 'Necesito el n\\u00famero de cotizaci\\u00f3n (formato COT-XXXX-XXXXX) para procesar el pago.';",
  "}",
  "",
  "// El total NO se incluye en el marcador: siempre se leer\\u00e1 desde la base de datos.",
  "return '[PAGAR_MP:numero=' + numero.toUpperCase() + ']';"
].join('\n');

const NEW_GENERAR_PAGO_MP = [
  "const agentOutput = $input.first().json;",
  "const message = String(agentOutput.output || '');",
  "",
  "// Solo actuar si hay marker de pago",
  "const pagoMatch = message.match(/\\[PAGAR_MP:numero=([^,\\s\\]]+)[^\\]]*\\]/);",
  "if (!pagoMatch) {",
  "  return [{ json: agentOutput }];",
  "}",
  "",
  "const numero   = pagoMatch[1].trim().replace(/['\"]/g, '').toUpperCase();",
  "const row      = agentOutput._quote_data;",
  "const MP_TOKEN = '$env.MERCADOPAGO_ACCESS_TOKEN';",
  "",
  "// SEGURIDAD: total SIEMPRE desde la base de datos, nunca del mensaje del LLM",
  "if (!row || !row.total || parseInt(row.total) <= 0) {",
  "  const errMsg = '\\u26a0\\ufe0f No se pudo verificar el monto de la cotizaci\\u00f3n ' + numero + ' en nuestra base de datos. Por favor contacta a soporte.';",
  "  return [{ json: { ...agentOutput, output: errMsg } }];",
  "}",
  "const total = parseInt(row.total);",
  "",
  "const fmt = n => Number(n).toLocaleString('es-CL');",
  "",
  "let paymentUrl = '';",
  "try {",
  "  const resp = await this.helpers.httpRequest({",
  "    method: 'POST',",
  "    url: 'https://api.mercadopago.com/checkout/preferences',",
  "    headers: { 'Authorization': 'Bearer ' + MP_TOKEN },",
  "    json: true,",
  "    body: {",
  "      items: [{",
  "        id: numero,",
  "        title: 'Cotizacion ' + numero + ' - Cesped Sintetico ARM',",
  "        quantity: 1,",
  "        unit_price: total,",
  "        currency_id: 'CLP'",
  "      }],",
  "      external_reference: numero",
  "    }",
  "  });",
  "  paymentUrl = (resp.sandbox_init_point || resp.init_point || '').trim();",
  "} catch(e) {",
  "  console.error('MercadoPago error:', e.message);",
  "}",
  "",
  "let newOutput;",
  "if (paymentUrl) {",
  "  newOutput = '\\ud83d\\udcb3 Tu link de pago est\\u00e1 listo para la cotizaci\\u00f3n ' + numero + ':\\n' +",
  "    '\\ud83d\\udc64 ' + (row.nombre || '') + '\\n' +",
  "    '\\ud83d\\udccd ' + (row.direccion || '') + '\\n' +",
  "    '\\ud83c\\udf3f ' + (row.producto || '') + ' \\u2014 ' + (row.m2 || 0) + ' m\\u00b2\\n' +",
  "    '\\ud83d\\udcb0 Total: $' + fmt(total) + '\\n\\n' +",
  "    '[PAYMENT_URL:' + paymentUrl + ']';",
  "} else {",
  "  newOutput = '\\ud83d\\udcb3 Hubo un error generando el link para ' + numero + '. Por favor intenta nuevamente o contacta a soporte.';",
  "}",
  "",
  "return [{ json: { ...agentOutput, output: newOutput, _mp_url: paymentUrl, _total: total, _quote_data: row } }];"
].join('\n');

let changes = 0;
wf.nodes.forEach(n => {
  if (n.name === 'Tool generar_pago') {
    n.parameters.jsCode = NEW_TOOL_GENERAR_PAGO;
    console.log('OK Tool generar_pago actualizado');
    changes++;
  }
  if (n.name === 'Generar Pago MP') {
    n.parameters.jsCode = NEW_GENERAR_PAGO_MP;
    console.log('OK Generar Pago MP actualizado (total desde BD)');
    changes++;
  }
});

fs.writeFileSync(WF_PATH, JSON.stringify(wf, null, 2), 'utf8');
console.log(changes + ' nodos actualizados.');
