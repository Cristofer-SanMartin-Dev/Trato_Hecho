import json, os

PATH = os.path.join(os.path.dirname(__file__), "n8n", "Trato Hecho - Chat Agent (2).json")

NEW_CODE = r"""const extract    = $('Extraer Input').first().json;
const redisQuote = $input.first().json;
const { uuid, message } = extract;

// 1. PARSEAR HISTORIAL
let history = [];
try {
  const raw = $('Obtener Historial Redis').first()?.json?.value;
  if (raw) history = typeof raw === 'string' ? JSON.parse(raw) : raw;
} catch(e) { history = []; }
if (!Array.isArray(history) || history.length === 0) {
  try {
    const bh = extract.bodyHistory;
    if (Array.isArray(bh) && bh.length > 0) history = bh;
  } catch(e2) {}
}
if (!Array.isArray(history)) history = [];
history = history.filter(m => m && m.content);

const msgLower      = message.toLowerCase().trim();
const allText       = history.map(m => m.content).join(' ').toLowerCase();
const lastAssistant = [...history].reverse().find(m => m.role === 'assistant')?.content?.toLowerCase() || '';

// 2. RECUPERAR DATOS YA CAPTURADOS emparejando pregunta->respuesta en historial
let nombreCapturado    = '';
let rutCapturado       = '';
let direccionCapturada = '';

for (let i = 0; i < history.length - 1; i++) {
  const msg      = history[i];
  const siguiente = history[i + 1];
  if (msg.role !== 'assistant' || siguiente.role !== 'user') continue;
  const pregunta = msg.content.toLowerCase();
  const respuesta = siguiente.content.trim();
  if (pregunta.includes('nombre completo') || pregunta.includes('tu nombre')) {
    nombreCapturado = respuesta;
  } else if (pregunta.includes('rut') && !pregunta.includes('direcci')) {
    rutCapturado = respuesta;
  } else if (pregunta.includes('direcci')) {
    direccionCapturada = respuesta;
  }
}

// 3. DETECTAR ESTADO ACTUAL
const estadoPidiendoNombre    = lastAssistant.includes('nombre completo') || lastAssistant.includes('tu nombre');
const estadoPidiendoRut       = lastAssistant.includes('rut') && !lastAssistant.includes('direcci');
const estadoPidiendoDireccion = lastAssistant.includes('direcci');
const estadoEnDatos           = estadoPidiendoNombre || estadoPidiendoRut || estadoPidiendoDireccion;
const estadoPidiendoInstalacion = lastAssistant.includes('instalaci') &&
  (lastAssistant.includes('si o no') || lastAssistant.includes('+$4.500') || lastAssistant.includes('responde s'));

// 4. DETECTAR PRODUCTO (la mencion mas reciente del historial gana)
let productoNombre = '';
let precioPorM2    = 0;
const todosTextos = [...history.map(m => m.content.toLowerCase()), msgLower];
for (let ti = todosTextos.length - 1; ti >= 0; ti--) {
  const tt = todosTextos[ti];
  if (tt.includes('luxury') || tt.includes('emerald') || tt.includes('40mm')) { productoNombre = 'Luxury Emerald (40mm)'; precioPorM2 = 28500; break; }
  if (tt.includes('soft touch') || (tt.includes('soft') && !tt.includes('luxury')) || tt.includes('30mm')) { productoNombre = 'Soft Touch (30mm)'; precioPorM2 = 22900; break; }
  if (tt.includes('pet') || tt.includes('friendly') || tt.includes('antimicrobial') || tt.includes('mascota')) { productoNombre = 'Pet-Friendly Turf (35mm)'; precioPorM2 = 26000; break; }
  if (tt.includes('futbol') || tt.includes('f\u00fatbol') || tt.includes('football') || tt.includes('fut') || tt.includes('cancha')) { productoNombre = 'Pasto Deportivo F\u00fatbol'; precioPorM2 = 0; break; }
  if (tt.includes('tenis') || tt.includes('padel') || tt.includes('p\u00e1del')) { productoNombre = 'Pasto Tenis & P\u00e1del'; precioPorM2 = 0; break; }
}

// 5. DETECTAR METROS (solo si NO estamos capturando datos)
let m2Valor = 0, esNumero = false, esDimensiones = false, dimTexto = '';
if (!estadoEnDatos) {
  const regexDim = /^([\d]+([.,][\d]+)?)\s*(x|por|\*)\s*([\d]+([.,][\d]+)?)\s*(m2|m|mt2|mt|mts|metros?)?$/i;
  const matchDim = message.trim().match(regexDim);
  if (matchDim) {
    const largo = parseFloat(matchDim[1].replace(',', '.'));
    const ancho = parseFloat(matchDim[4].replace(',', '.'));
    m2Valor = Math.round(largo * ancho * 100) / 100;
    esNumero = true; esDimensiones = true;
    dimTexto = largo + ' x ' + ancho;
  } else {
    const regexMetros = /^([\d]+([.,][\d]+)?)(\s*(m2|m|mt2|mt|mts|metros?))?$/i;
    const matchMetros = message.trim().match(regexMetros);
    if (matchMetros) { m2Valor = parseFloat(matchMetros[1].replace(',', '.')); esNumero = true; }
  }
}
let m2EnHistorial = 0;
const matchM2Hist = allText.match(/([\d]+([.,][\d]+)?)\s*(m2|mt2|mt|mts|metros?)/i);
if (matchM2Hist) m2EnHistorial = parseFloat(matchM2Hist[1].replace(',', '.'));
if (!m2EnHistorial) {
  const mDH = allText.match(/([\d]+([.,][\d]+)?)\s*(x|por|\*)\s*([\d]+([.,][\d]+)?)/i);
  if (mDH) m2EnHistorial = Math.round(parseFloat(mDH[1].replace(',','.')) * parseFloat(mDH[4].replace(',','.')) * 100) / 100;
}
const m2Final = m2Valor > 0 ? m2Valor : m2EnHistorial;

// 6. DETECTAR INSTALACION emparejando pregunta->respuesta
let instalacionDefinida = null;
for (let i = 0; i < history.length - 1; i++) {
  const msg = history[i];
  const siguiente = history[i + 1];
  if (msg.role !== 'assistant' || siguiente.role !== 'user') continue;
  const pregunta = msg.content.toLowerCase();
  if (pregunta.includes('instalaci') && (pregunta.includes('si o no') || pregunta.includes('+$4.500') || pregunta.includes('responde s'))) {
    const resp = siguiente.content.toLowerCase().trim();
    if (resp === 'si' || resp === 'yes' || resp.includes('con instalaci')) instalacionDefinida = true;
    else if (resp === 'no' || resp.includes('sin instalaci')) instalacionDefinida = false;
  }
}
if (estadoPidiendoInstalacion) {
  if (msgLower === 'si' || msgLower === 'yes') instalacionDefinida = true;
  else if (msgLower === 'no') instalacionDefinida = false;
}

// 7. CALCULAR
let m2Margen = 0, subtotalPasto = 0, subtotalInst = 0, totalFinal = 0;
if (productoNombre && m2Final > 0 && precioPorM2 > 0) {
  m2Margen      = Math.ceil(m2Final * 1.10);
  subtotalPasto = m2Margen * precioPorM2;
  subtotalInst  = instalacionDefinida === true ? m2Margen * 4500 : 0;
  totalFinal    = subtotalPasto + subtotalInst;
}

// 8. INSTRUCCION INMEDIATA
let instruccionInmediata = '';

if (estadoEnDatos) {
  let nombreFinal    = nombreCapturado;
  let rutFinal       = rutCapturado;
  let direccionFinal = direccionCapturada;

  if (estadoPidiendoNombre) {
    nombreFinal = message.trim();
    instruccionInmediata = `
INSTRUCCION CRITICA - OBLIGATORIA:
Estamos recopilando datos de cotizacion. El cliente dio su nombre: "${nombreFinal}".
NO saludar. NO preguntar por cesped. NO reiniciar flujo.
Responde SOLO esta frase exacta: "Perfecto ${nombreFinal}! Ahora necesito tu RUT."`;

  } else if (estadoPidiendoRut) {
    rutFinal = message.trim();
    instruccionInmediata = `
INSTRUCCION CRITICA - OBLIGATORIA:
Estamos recopilando datos de cotizacion. El cliente dio su RUT: "${rutFinal}".
NO saludar. NO preguntar por cesped. NO reiniciar flujo.
Responde SOLO esta frase exacta: "Gracias! Por ultimo, cual es tu direccion de instalacion?"`;

  } else if (estadoPidiendoDireccion) {
    direccionFinal = message.trim();
    instruccionInmediata = `
INSTRUCCION CRITICA - OBLIGATORIA:
El cliente completo todos los datos para la cotizacion.
Nombre: ${nombreFinal || 'ver historial'}
RUT: ${rutFinal || 'ver historial'}
Direccion: ${direccionFinal}
Producto: ${productoNombre}
m2 con margen: ${m2Margen}
Instalacion: ${instalacionDefinida === true ? 'SI' : 'NO'}
Total: ${totalFinal}

Genera UNICAMENTE esta etiqueta sin ningun texto adicional:
[COTIZAR: nombre=${nombreFinal}, rut=${rutFinal}, direccion=${direccionFinal}, m2=${m2Margen}, tipo=${productoNombre}, instalacion=${instalacionDefinida === true ? 'SI' : 'NO'}, total=${totalFinal}]`;
  }

} else if (msgLower === 'cotizar') {
  instruccionInmediata = `
INSTRUCCION CRITICA - OBLIGATORIA:
El cliente quiere cotizacion formal.
Responde SOLO: "Perfecto! Para generar tu cotizacion necesito algunos datos. Cual es tu nombre completo?"`;

} else if (productoNombre && esNumero && m2Valor > 0 && precioPorM2 > 0) {
  const origenM2 = esDimensiones ? dimTexto + ' m = ' + m2Valor + ' m2' : m2Valor + ' m2';
  instruccionInmediata = `
INSTRUCCION CRITICA - OBLIGATORIA:
El cliente eligio "${productoNombre}" y acaba de indicar ${origenM2}.
Responde EXACTAMENTE:

Para ${m2Valor} m2 de ${productoNombre}${esDimensiones ? ' (' + dimTexto + ' m)' : ''}:
m2 con margen tecnico (10%): ${m2Margen} m2
Subtotal pasto: $${subtotalPasto.toLocaleString('es-CL')}
Necesitas instalacion? (+$4.500/m2) Responde SI o NO.`;

} else if (productoNombre && esNumero && m2Valor > 0 && precioPorM2 === 0) {
  instruccionInmediata = `
INSTRUCCION CRITICA - OBLIGATORIA:
El cliente eligio "${productoNombre}" (precio a cotizar segun proyecto) e indic\u00f3 ${m2Valor} m2.
Responde: "Para ${productoNombre} con ${m2Valor} m2, el precio depende del proyecto. Escribe COTIZAR para que un asesor te contacte con precio exacto."`;

} else if (instalacionDefinida !== null && totalFinal > 0 && estadoPidiendoInstalacion) {
  const lineaInst = instalacionDefinida
    ? `Instalacion (${m2Margen} m2): $${subtotalInst.toLocaleString('es-CL')}`
    : `Sin instalacion`;
  instruccionInmediata = `
INSTRUCCION CRITICA - OBLIGATORIA:
Responde EXACTAMENTE:

Resumen de tu pedido:
${productoNombre} - ${m2Margen} m2 (con margen 10%)
Subtotal pasto: $${subtotalPasto.toLocaleString('es-CL')}
${lineaInst}
TOTAL ESTIMADO: $${totalFinal.toLocaleString('es-CL')}

Deseas una cotizacion formal? Escribe COTIZAR.`;
}

// 9. COTIZACION EXISTENTE
let quoteContext = '';
try {
  const rawQ = redisQuote?.value ?? redisQuote?.data ?? null;
  if (rawQ) {
    const q = typeof rawQ === 'string' ? JSON.parse(rawQ) : rawQ;
    quoteContext = `\nCOTIZACION N${q.numero} ya generada. Total: $${q.total.toLocaleString('es-CL')}. Para pagar: [PAGAR: numero=${q.numero}, monto=${q.total}]`;
  }
} catch(e) {}

// 10. SYSTEM PROMPT
const systemPrompt = `Eres Queno, vendedor virtual de Cesped Sintetico ARM, Melipilla.
${instruccionInmediata}

CATALOGO (CLP/m2):
- Luxury Emerald (40mm): $28.500/m2 - jardin/terraza premium
- Soft Touch (30mm): $22.900/m2 - jardin residencial suave
- Pet-Friendly Turf (35mm): $26.000/m2 - jardin con mascotas, antimicrobial
- Pasto Deportivo Futbol: precio a cotizar - canchas futbol 11 y 7
- Pasto Tenis & Padel: precio a cotizar - canchas tenis y padel
- Instalacion opcional: +$4.500/m2 (solo aplica a productos con precio fijo)
- Siempre aplicar 10% margen tecnico sobre m2 solicitados.

FLUJO (solo si NO hay instruccion critica arriba):
1. Sin producto: pregunta uso (jardin/terraza o cancha deportiva) y muestra opciones con precios. Jardin: Luxury Emerald $28.500, Soft Touch $22.900, Pet-Friendly $26.000. Deportivo: Futbol 11&7 y Tenis/Padel (precio a cotizar).
2. Con producto, sin m2: pregunta cuantos m2 necesita. Acepta tanto un numero como "largo x ancho".
3. Con producto + m2: usa SOLO el subtotal calculado por el sistema en la INSTRUCCION CRITICA.
4. Con instalacion definida: muestra el TOTAL del sistema. Di "Escribe COTIZAR para cotizacion formal".
5. Cliente escribe COTIZAR: pregunta nombre completo.
6. Tras nombre: pregunta RUT (formato chileno, ej: 12.345.678-9).
7. Tras RUT: pregunta direccion de instalacion completa.
8. Tras direccion: emite SOLO la etiqueta sin ningun texto antes ni despues:
[COTIZAR: nombre=X, rut=X, direccion=X, m2=X, tipo=X, instalacion=SI/NO, total=X]

MEDIDAS - Como interpretar lo que dice el cliente:
- Numero solo (20) o con unidad (20m2, 20 metros) = m2 directamente.
- Dos numeros con x/por (5x8, 5 por 8, 5*8) = el sistema ya calculo m2=largo x ancho, usa ese resultado.
- Si el cliente da largo y ancho en texto libre ("tengo 5 de largo y 8 de ancho"), confirma: "Son X m2 en total?"
- EXCEPCION: en modo nombre/RUT/direccion, NUNCA interpretes texto ni numeros como m2.

CAMBIO DE PRODUCTO:
- Si el cliente menciona un producto diferente al anterior, el sistema ya lo detecto. Confirma el cambio.
- Ejemplo: "Perfecto, cambiamos a [nuevo producto]. Los mismos m2?"

HILO DE CONVERSACION:
- Si el cliente hace una pregunta fuera de contexto (como pedir ayuda para medir, preguntar algo general), responde brevemente y RETOMA el punto exacto donde estabas.
- Ejemplo: si estabas preguntando cuantos m2 y el cliente dice "no se me ayudas a medir", explica brevemente como medir y vuelve a preguntar los m2.
- NUNCA abandones el producto o datos ya capturados por una pregunta off-topic.
- NUNCA reinicies el flujo si ya hay un producto seleccionado.

REGLAS:
- Maximo 4 lineas por respuesta. Solo 1 pregunta por mensaje.
- NUNCA saludar si ya hay historial.
- NUNCA reiniciar flujo si ya hay producto o datos.
- NUNCA pedir datos ya entregados.
- Si hay INSTRUCCION CRITICA arriba: SIGUE SOLO ESA INSTRUCCION, sin agregar texto extra.
- NUNCA mostrar datos de cotizacion una vez confirmada y enviada.
- NUNCA calcular totales tu mismo: usa SIEMPRE los valores de la INSTRUCCION CRITICA.
- Si un numero parece fuera de rango (menor a 1 o mayor a 1000 m2), pide confirmacion antes de continuar.
- Si el cliente dice que no sabe sus medidas o no sabe cuanto tiene, explica brevemente como medir y agrega al final de tu respuesta exactamente: [CALCULAR]

ERRORES FRECUENTES A EVITAR:
- No pedir nombre/RUT/direccion si ya estan en el historial previo.
- No saludar con "Hola" ni reiniciar la conversacion si ya hay mensajes.
- No calcular totales propios; usa solo los valores calculados por el sistema.
- No agregar texto antes o despues de [COTIZAR:] cuando el sistema lo indica.
- No interpretar un RUT o numero de telefono como metros cuadrados.
- No olvidar preguntar instalacion antes de mostrar el TOTAL.
- No mostrar los datos de la cotizacion una vez confirmada y enviada.
${quoteContext}`;

// 11. MENSAJES
const messages = [
  ...history.map(m => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content })),
  { role: 'user', content: message }
];

// 12. BODY PARA CLAUDE API
const claudeBody = JSON.stringify({
  model: "claude-sonnet-4-5",
  max_tokens: 1024,
  system: systemPrompt,
  messages
});

return [{
  json: {
    uuid, message, systemPrompt, messages, claudeBody,
    historyLength: history.length,
    productoDetectado: productoNombre,
    m2Detectado: m2Final,
    m2ConMargen: m2Margen,
    totalFinal,
    instalacionDefinida,
    esNumero,
    estadoEnDatos,
    nombreCapturado,
    rutCapturado,
    direccionCapturada
  }
}];
"""

with open(PATH, encoding="utf-8") as f:
    data = json.load(f)

node = next(n for n in data["nodes"] if n["name"] == "Construir Prompt Claude")
node["parameters"]["jsCode"] = NEW_CODE
print(f"Node found: {node['name']} (id: {node['id']})")

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("OK - workflow updated")
