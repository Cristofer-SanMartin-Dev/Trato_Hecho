# =============================================================
# update_agent.ps1  -  Mejoras al nodo "Construir Prompt Claude"
# =============================================================
# Cambios aplicados:
#   1. Deteccion de producto: la mencion MAS RECIENTE gana
#   2. Deteccion de metros: agrega soporte para "largo x ancho"
#   3. instruccionInmediata de m2: muestra origen de las dimensiones
#   4. System prompt: reglas mejoradas + seccion MEDIDAS + ERRORES FRECUENTES
# =============================================================

$filePath = "c:\Users\prueba\Downloads\Trato_Hecho-main\Trato_Hecho-main\n8n\Trato Hecho - Chat Agent (2).json"

# --- Leer y parsear el JSON ---
$json = Get-Content $filePath -Raw -Encoding UTF8 | ConvertFrom-Json

$node = $json.nodes | Where-Object { $_.name -eq 'Construir Prompt Claude' }
if (-not $node) { Write-Error "ERROR: Nodo 'Construir Prompt Claude' no encontrado"; exit 1 }

$code = $node.parameters.jsCode
Write-Host "Codigo original: $($code.Length) chars"

# Normalizar a LF solamente (evita problemas CRLF vs LF)
function Normalize { param([string]$s) return $s.Replace("`r`n", "`n").TrimEnd() }

$code = $code.Replace("`r`n", "`n")

# =============================================================
# REEMPLAZO 1: Deteccion de producto (mas reciente primero)
# =============================================================
$old1 = Normalize @'
// 4. DETECTAR PRODUCTO
let productoNombre = '';
let precioPorM2    = 0;
const textoTotal   = allText + ' ' + msgLower;
if (textoTotal.includes('sico') || textoTotal.includes('20mm') || textoTotal.includes('pasto b')) {
  productoNombre = 'Pasto Basico (20mm)';   precioPorM2 = 8500;
} else if (textoTotal.includes('premium') || textoTotal.includes('35mm')) {
  productoNombre = 'Pasto Premium (35mm)';  precioPorM2 = 15000;
} else if (textoTotal.includes('deportivo') || textoTotal.includes('25mm')) {
  productoNombre = 'Pasto Deportivo (25mm)'; precioPorM2 = 12000;
}
'@

$new1 = Normalize @'
// 4. DETECTAR PRODUCTO (la mencion mas reciente del historial gana)
let productoNombre = '';
let precioPorM2    = 0;
// Iterar del mensaje mas reciente al mas antiguo; el primer match es el producto activo
const todosTextos = [...history.map(m => m.content.toLowerCase()), msgLower];
for (let ti = todosTextos.length - 1; ti >= 0; ti--) {
  const tt = todosTextos[ti];
  if (tt.includes('premium') || tt.includes('35mm')) { productoNombre = 'Pasto Premium (35mm)'; precioPorM2 = 15000; break; }
  if (tt.includes('deportivo') || tt.includes('25mm')) { productoNombre = 'Pasto Deportivo (25mm)'; precioPorM2 = 12000; break; }
  if (tt.includes('basico') || tt.includes('sico') || tt.includes('20mm') || tt.includes('pasto b')) { productoNombre = 'Pasto Basico (20mm)'; precioPorM2 = 8500; break; }
}
'@

if ($code.Contains($old1)) {
    $code = $code.Replace($old1, $new1)
    Write-Host "OK Reemplazo 1 aplicado: deteccion de producto mas reciente"
} else {
    Write-Warning "FALLO Reemplazo 1 no encontrado (puede que ya este aplicado)"
}

# =============================================================
# REEMPLAZO 2: Deteccion de metros (largo x ancho)
# =============================================================
$old2 = Normalize @'
// 5. DETECTAR METROS (solo si NO estamos capturando datos)
const regexMetros = /^([\d]+([.,][\d]+)?)(\s*(m2|m|mt2|mt|mts|metros?))?$/i;
const matchMetros = !estadoEnDatos ? message.trim().match(regexMetros) : null;
const esNumero    = !!matchMetros;
const m2Valor     = esNumero ? parseFloat(matchMetros[1].replace(',', '.')) : 0;

let m2EnHistorial = 0;
const matchM2Hist = allText.match(/([\d]+([.,][\d]+)?)\s*(m2|m|mt2|mt|mts|metros?)/i);
if (matchM2Hist) m2EnHistorial = parseFloat(matchM2Hist[1].replace(',', '.'));
const m2Final = m2Valor > 0 ? m2Valor : m2EnHistorial;
'@

$new2 = Normalize @'
// 5. DETECTAR METROS (solo si NO estamos capturando datos)
let m2Valor = 0, esNumero = false, esDimensiones = false, dimTexto = '';
if (!estadoEnDatos) {
  // 5a. Detectar largo x ancho: "5x8", "5 x 8", "5 por 8", "5*8", "5.5 por 3"
  const regexDim = /^([\d]+([.,][\d]+)?)\s*(x|por|\*)\s*([\d]+([.,][\d]+)?)\s*(m2|m|mt2|mt|mts|metros?)?$/i;
  const matchDim = message.trim().match(regexDim);
  if (matchDim) {
    const largo = parseFloat(matchDim[1].replace(',', '.'));
    const ancho = parseFloat(matchDim[4].replace(',', '.'));
    m2Valor = Math.round(largo * ancho * 100) / 100;
    esNumero = true; esDimensiones = true;
    dimTexto = largo + ' x ' + ancho;
  } else {
    // 5b. Numero solo o con unidad de area
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
'@

if ($code.Contains($old2)) {
    $code = $code.Replace($old2, $new2)
    Write-Host "OK Reemplazo 2 aplicado: deteccion largo x ancho"
} else {
    Write-Warning "FALLO Reemplazo 2 no encontrado (puede que ya este aplicado)"
}

# =============================================================
# REEMPLAZO 3: instruccionInmediata para m2 (mostrar dimensiones)
# =============================================================
$old3 = Normalize @'
} else if (productoNombre && esNumero && m2Valor > 0) {
  instruccionInmediata = `
INSTRUCCION CRITICA - OBLIGATORIA:
El cliente eligio "${productoNombre}" y acaba de indicar ${m2Valor} m2.
Responde EXACTAMENTE:

Para ${m2Valor} m2 de ${productoNombre}:
m2 con margen tecnico (10%): ${m2Margen} m2
Subtotal pasto: $${subtotalPasto.toLocaleString('es-CL')}
Necesitas instalacion? (+$4.500/m2) Responde SI o NO.`;
'@

$new3 = Normalize @'
} else if (productoNombre && esNumero && m2Valor > 0) {
  const origenM2 = esDimensiones ? dimTexto + ' m = ' + m2Valor + ' m2' : m2Valor + ' m2';
  instruccionInmediata = `
INSTRUCCION CRITICA - OBLIGATORIA:
El cliente eligio "${productoNombre}" y acaba de indicar ${origenM2}.
Responde EXACTAMENTE:

Para ${m2Valor} m2 de ${productoNombre}${esDimensiones ? ' (' + dimTexto + ' m)' : ''}:
m2 con margen tecnico (10%): ${m2Margen} m2
Subtotal pasto: $${subtotalPasto.toLocaleString('es-CL')}
Necesitas instalacion? (+$4.500/m2) Responde SI o NO.`;
'@

if ($code.Contains($old3)) {
    $code = $code.Replace($old3, $new3)
    Write-Host "OK Reemplazo 3 aplicado: instruccionInmediata con dimensiones"
} else {
    Write-Warning "FALLO Reemplazo 3 no encontrado"
}

# =============================================================
# REEMPLAZO 4: System prompt - FLUJO + MEDIDAS + REGLAS mejoradas
# =============================================================
$old4 = Normalize @'
FLUJO (solo si NO hay instruccion critica arriba):
1. Sin producto: pregunta jardin/terraza o deportivo + muestra 3 opciones numeradas.
2. Con producto sin m2: pregunta cuantos m2 necesita.
3. Con producto + m2: muestra subtotal y pregunta instalacion (SI o NO).
4. Con instalacion definida: muestra TOTAL y dice escribe COTIZAR para cotizacion formal.
5. Cliente escribe COTIZAR: pregunta nombre completo.
6. Tras nombre: pregunta RUT.
7. Tras RUT: pregunta direccion de instalacion.
8. Tras direccion: genera [COTIZAR: nombre=X, rut=X, direccion=X, m2=X, tipo=X, instalacion=SI/NO, total=X]
9. Tras tener todos los datos ya ingresados preguntar si confirma cotizacion si/no? cambiar accion a COTIZAR
10.Tras confirmar la cotizacion 


INTERPRETACION DE MEDIDAS: numero solo o con unidades = m2. Ejemplo: 12, 12m, 12mt, 12m2, 12 metros.
EXCEPCION: si estamos capturando nombre/RUT/direccion NO interpretes como m2.

REGLAS:
- Maximo 4 lineas por respuesta. Solo 1 pregunta por mensaje.
- NUNCA saludar si ya hay historial.
- NUNCA reiniciar flujo si ya hay producto o datos.
- NUNCA pedir datos ya entregados.
- Si hay instruccion critica arriba: SIGUE SOLO ESA INSTRUCCION.
- NUNCA pedir datos ya entregados una vez confirmada la COTIZACION.
- NUNA MOSTRAR DATOS DE COTIZACION UNA VEZ COFIRMADA Y ENVIADA
'@

$new4 = Normalize @'
FLUJO (solo si NO hay instruccion critica arriba):
1. Sin producto: pregunta uso (jardin/terraza/cancha) y muestra 3 opciones numeradas con precios.
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

REGLAS:
- Maximo 4 lineas por respuesta. Solo 1 pregunta por mensaje.
- NUNCA saludar si ya hay historial.
- NUNCA reiniciar flujo si ya hay producto o datos.
- NUNCA pedir datos ya entregados.
- Si hay INSTRUCCION CRITICA arriba: SIGUE SOLO ESA INSTRUCCION, sin agregar texto extra.
- NUNCA mostrar datos de cotizacion una vez confirmada y enviada.
- NUNCA calcular totales tu mismo: usa SIEMPRE los valores de la INSTRUCCION CRITICA.
- Si un numero parece fuera de rango (menor a 1 o mayor a 1000 m2), pide confirmacion antes de continuar.

ERRORES FRECUENTES A EVITAR:
- No pedir nombre/RUT/direccion si ya estan en el historial previo.
- No saludar con "Hola" ni reiniciar la conversacion si ya hay mensajes.
- No calcular totales propios; usa solo los valores calculados por el sistema.
- No agregar texto antes o despues de [COTIZAR:] cuando el sistema lo indica.
- No interpretar un RUT o numero de telefono como metros cuadrados.
- No olvidar preguntar instalacion antes de mostrar el TOTAL.
- No mostrar los datos de la cotizacion una vez confirmada y enviada.
'@

if ($code.Contains($old4)) {
    $code = $code.Replace($old4, $new4)
    Write-Host "OK Reemplazo 4 aplicado: system prompt mejorado"
} else {
    Write-Warning "FALLO Reemplazo 4 no encontrado"
}

# =============================================================
# Guardar resultado
# =============================================================
$node.parameters.jsCode = $code
Write-Host "Codigo actualizado: $($code.Length) chars"

# Serializar con profundidad suficiente
$newJson = $json | ConvertTo-Json -Depth 20

# Guardar con codificacion UTF-8 sin BOM
[System.IO.File]::WriteAllText($filePath, $newJson, [System.Text.Encoding]::UTF8)

Write-Host ""
Write-Host "============================================"
Write-Host " Archivo actualizado: $filePath"
Write-Host "============================================"
