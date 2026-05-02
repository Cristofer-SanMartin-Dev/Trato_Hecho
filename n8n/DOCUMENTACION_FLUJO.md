# Documentación Técnica — Flujo n8n "Trato Hecho - Chat Agent"

> Versión analizada: `Trato Hecho - Chat Agent (2).json`  
> Fecha de documentación: Mayo 2026

---

## Índice

1. [Arquitectura general del flujo](#1-arquitectura-general-del-flujo)
2. [Descripción detallada de cada bloque](#2-descripción-detallada-de-cada-bloque)
3. [Preguntas específicas de negocio y técnicas](#3-preguntas-específicas-de-negocio-y-técnicas)
4. [Problemas identificados y recomendaciones](#4-problemas-identificados-y-recomendaciones)

---

## 1. Arquitectura general del flujo

El flujo procesa cada mensaje del usuario en una secuencia lineal con ramificación al final según la intención detectada:

```
[Web] → Webhook Chat
          ↓
      Extraer Input
          ↓
  Obtener Historial Redis
          ↓
  Obtener Cotización Redis
          ↓
  Construir Prompt Claude   ← AQUÍ se calcula el total (no Claude)
          ↓
   Llamar Claude API
          ↓
  Parsear Respuesta Claude
          ↓
    Preparar Historial
          ↓
  Guardar Historial Redis
          ↓
      Switch Acción
       /    |    \
  COTIZAR PAGAR  CHAT
```

**Tres rutas de salida:**

| Acción | Ruta |
|--------|------|
| `COTIZAR` | Incrementar Contador → Crear Cotización → Guardar Redis → Respuesta → Telegram → Gmail → Webhook |
| `PAGAR` | If (monto > 0) → MercadoPago → Respuesta → Telegram → Gmail → Webhook |
| `CHAT` | Respuesta Simple → Webhook |

---

## 2. Descripción detallada de cada bloque

---

### Bloque 1 — `Webhook Chat`

| Campo | Detalle |
|-------|---------|
| **Tipo** | n8n-nodes-base.webhook |
| **Rol** | Punto de entrada del flujo. Recibe los mensajes desde la interfaz web del chatbot. |
| **Recibe** | Petición HTTP POST al path `/chat` |
| **Transforma** | Nada. Solo pasa el body completo al siguiente nodo. |
| **Entrega** | El objeto `body` crudo al nodo `Extraer Input` |
| **Regla de negocio** | CORS abierto (`*`). El modo de respuesta es `responseNode`, lo que significa que la respuesta HTTP real la envía un nodo posterior (`Responder Webhook`), no este nodo. |

**Cómo se recibe el mensaje del usuario desde la web:**  
La web hace un `POST` a la URL del webhook con un cuerpo JSON que debe incluir dos campos:
- `message` (o `chatInput`): el texto que escribió el usuario.
- `sessionId` (o `uuid`): identificador único de la conversación. Si no se envía, se genera uno automático con timestamp + string aleatorio.

Ejemplo de cuerpo esperado:
```json
{
  "sessionId": "usuario-abc-123",
  "message": "Quiero pasto premium para 20m2"
}
```

---

### Bloque 2 — `Extraer Input`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Code (JavaScript) |
| **Rol** | Normalizar y validar la entrada del usuario. |
| **Recibe** | El objeto raw del body del webhook (puede tener estructura `body.message` o directamente `message`). |
| **Transforma** | Extrae `uuid` y `message`. Si no hay `sessionId`/`uuid`, genera uno automático. Si `message` está vacío, lanza error. |
| **Entrega** | `{ uuid, message }` limpio al siguiente nodo. |
| **Regla de negocio** | El campo `message` es obligatorio. Sin él, el flujo falla con error controlado `"message es requerido"`. |

**Código clave:**
```js
const uuid = String(body.sessionId || body.uuid || '').trim()
           || 'auto_' + Date.now() + '_' + Math.random().toString(36).substr(2,6);
const message = String(body.message || body.chatInput || '').trim();
if (!message) throw new Error('message es requerido');
```

---

### Bloque 3 — `Obtener Historial Redis`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Redis GET |
| **Rol** | Recuperar el historial de conversación de esta sesión. |
| **Recibe** | `uuid` del nodo `Extraer Input`. |
| **Transforma** | Lee la clave `hist_{uuid}` de Redis. |
| **Entrega** | El valor almacenado (string JSON) o `null` si no existe. |
| **Regla de negocio** | TTL del historial: 24 horas (86.400 segundos). Si la clave no existe o expiró, el flujo continúa con historial vacío. |

**Qué información se consulta en Redis y para qué:**  
- **Clave:** `hist_{uuid}` (ej: `hist_usuario-abc-123`)  
- **Contenido:** Array JSON con los últimos 20 turnos de conversación, cada uno con `{ role: "user"|"assistant", content: "texto" }`.  
- **Propósito:** Que Claude tenga contexto de lo que ya se habló, para no volver a preguntar datos ya entregados (producto, m2, nombre, RUT, dirección) y para que el nodo `Construir Prompt Claude` pueda recuperar esos datos del historial.

---

### Bloque 4 — `Obtener Cotización Redis`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Redis GET (con salida de error alternativa) |
| **Rol** | Verificar si ya existe una cotización formal generada para esta sesión. |
| **Recibe** | `uuid` del nodo `Extraer Input`. |
| **Transforma** | Lee la clave `th:quote:{uuid}` de Redis. |
| **Entrega** | El objeto cotización serializado (JSON string) o `null`. |
| **Regla de negocio** | Si falla la lectura (error de conexión, clave inexistente), el flujo continúa igual (salida de error alternativa configurada). TTL de cotizaciones: 10 días (864.000 segundos). |

**Para qué se usa la cotización en Redis:**  
Si existe una cotización previa, el nodo `Construir Prompt Claude` agrega al system prompt el siguiente contexto:
```
COTIZACION N° {numero} ya generada. Total: ${total}. Para pagar: [PAGAR: numero={numero}, monto={total}]
```
Esto permite que Claude informe al usuario que ya tiene una cotización y ofrezca el link de pago directamente.

---

### Bloque 5 — `Construir Prompt Claude` ⭐ (Bloque central)

| Campo | Detalle |
|-------|---------|
| **Tipo** | Code (JavaScript) |
| **Rol** | Cerebro lógico del flujo. Determina el estado de la conversación, **calcula el total**, construye el system prompt y arma el body para la API de Claude. |
| **Recibe** | `uuid`, `message` (de `Extraer Input`); historial (de `Obtener Historial Redis`); cotización previa (de `Obtener Cotización Redis`). |
| **Transforma** | Ver subsecciones a continuación. |
| **Entrega** | `claudeBody` (JSON para API Anthropic), `systemPrompt`, `messages`, y variables de diagnóstico. |
| **Regla de negocio** | Todo el cálculo matemático ocurre aquí, no en Claude. |

#### 5.1 — Recuperación de datos del historial

El nodo recorre el historial buscando pares pregunta-respuesta (assistant → user) para recuperar:
- **Nombre:** si el mensaje del asistente contenía "nombre completo" o "tu nombre"
- **RUT:** si el mensaje del asistente contenía "rut" (sin "dirección")
- **Dirección:** si el mensaje del asistente contenía "direcci"

Esto permite que, aunque el usuario ya entregó su nombre hace 3 mensajes, el nodo lo recuerde sin depender solo de Claude.

#### 5.2 — Detección del estado actual

Se analiza el **último mensaje del asistente** para determinar en qué paso del flujo estamos:

| Variable | Condición detectada |
|----------|---------------------|
| `estadoPidiendoNombre` | El último mensaje pedía "nombre completo" o "tu nombre" |
| `estadoPidiendoRut` | El último mensaje pedía "rut" |
| `estadoPidiendoDireccion` | El último mensaje pedía "direcci" |
| `estadoEnDatos` | Cualquiera de los tres anteriores |
| `estadoPidiendoInstalacion` | El último mensaje mencionaba "instalaci" y ("si o no" o "+$4.500") |

#### 5.3 — Detección del producto

Se busca en el **texto completo** del historial + mensaje actual:

| Keyword detectado | Producto asignado | Precio/m² |
|-------------------|-------------------|-----------|
| `sico`, `20mm`, `pasto b` | Pasto Basico (20mm) | $8.500 |
| `premium`, `35mm` | Pasto Premium (35mm) | $15.000 |
| `deportivo`, `25mm` | Pasto Deportivo (25mm) | $12.000 |

**Limitación:** Si el usuario dice solo "el primero" o un nombre alternativo, no se detecta.

#### 5.4 — Detección de metros cuadrados

```js
const regexMetros = /^([\d]+([.,][\d]+)?)(\s*(m2|m|mt2|mt|mts|metros?))?$/i;
```

- **Solo funciona** si el mensaje del usuario es **únicamente un número** (opcionalmente con unidad de área).
- Ejemplos válidos: `20`, `20m2`, `20 metros`, `20,5 mt`
- Ejemplos **NO válidos**: `5 por 3`, `5x3`, `largo 5 ancho 3`, `tengo 5 metros de largo`
- **Si `estadoEnDatos` es true** (el sistema está capturando nombre/RUT/dirección), la detección de metros se desactiva para no confundir un RUT numérico con m2.

Si no hay m2 en el mensaje actual, busca en el historial con:
```js
/([\ d]+([.,][\d]+)?)\s*(m2|m|mt2|mt|mts|metros?)/i
```

#### 5.5 — Cálculo del total (realizado por el sistema, no por Claude)

```js
m2Margen      = Math.ceil(m2Final * 1.10)        // m² solicitados + 10%, redondeado hacia arriba
subtotalPasto = m2Margen * precioPorM2            // m² con margen × precio del producto
subtotalInst  = instalacionDefinida === true
                ? m2Margen * 4500 : 0             // instalación: $4.500/m²
totalFinal    = subtotalPasto + subtotalInst
```

**El cálculo completo es determinístico y lo realiza este nodo JavaScript, no Claude.**  
Claude recibe los valores ya calculados en la instrucción crítica y los debe repetir textualmente.

#### 5.6 — Construcción de la instrucción crítica (`instruccionInmediata`)

Dependiendo del estado detectado, se construye una instrucción que encabeza el system prompt y que Claude **debe seguir obligatoriamente** por encima de las reglas generales:

| Situación | Instrucción generada |
|-----------|----------------------|
| `estadoPidiendoNombre` + mensaje recibido | Claude debe preguntar el RUT con frase exacta |
| `estadoPidiendoRut` + mensaje recibido | Claude debe preguntar dirección con frase exacta |
| `estadoPidiendoDireccion` + mensaje recibido | Claude debe emitir `[COTIZAR: nombre=X, rut=X, ...]` con todos los datos y totales precalculados |
| Mensaje = `"cotizar"` | Claude debe iniciar captura de nombre |
| Producto detectado + número de m² recibido | Claude muestra el subtotal calculado y pregunta instalación |
| Instalación definida | Claude muestra el resumen total y dice que escriba COTIZAR |

#### 5.7 — System prompt completo enviado a Claude

```
Eres Queno, vendedor virtual de Cesped Sintetico ARM, Melipilla.
{instruccionInmediata}

CATALOGO (CLP/m2):
- Pasto Basico (20mm): $8.500/m2 - jardin/terraza
- Pasto Premium (35mm): $15.000/m2 - jardin premium
- Pasto Deportivo (25mm): $12.000/m2 - canchas/uso intensivo
- Instalacion opcional: +$4.500/m2
- Siempre aplicar 10% margen tecnico sobre m2 solicitados.

FLUJO (solo si NO hay instruccion critica arriba):
1. Sin producto: pregunta jardin/terraza o deportivo + muestra 3 opciones numeradas.
2. Con producto sin m2: pregunta cuantos m2 necesita.
3. Con producto + m2: muestra subtotal y pregunta instalacion (SI o NO).
4. Con instalacion definida: muestra TOTAL y dice escribe COTIZAR para cotizacion formal.
5. Cliente escribe COTIZAR: pregunta nombre completo.
6. Tras nombre: pregunta RUT.
7. Tras RUT: pregunta direccion de instalacion.
8. Tras direccion: genera [COTIZAR: nombre=X, rut=X, direccion=X, m2=X, tipo=X, instalacion=SI/NO, total=X]

INTERPRETACION DE MEDIDAS: numero solo o con unidades = m2.
EXCEPCION: si estamos capturando nombre/RUT/direccion NO interpretes como m2.

REGLAS:
- Maximo 4 lineas por respuesta. Solo 1 pregunta por mensaje.
- NUNCA saludar si ya hay historial.
- NUNCA reiniciar flujo si ya hay producto o datos.
- NUNCA pedir datos ya entregados.
- Si hay instruccion critica arriba: SIGUE SOLO ESA INSTRUCCION.
{quoteContext si hay cotización previa}
```

**Modelo usado:** `claude-sonnet-5-6`, `max_tokens: 1024`

---

### Bloque 6 — `Llamar Claude API`

| Campo | Detalle |
|-------|---------|
| **Tipo** | HTTP Request POST |
| **Rol** | Enviar el prompt a la API de Anthropic y obtener la respuesta de Claude. |
| **Recibe** | `claudeBody` del nodo anterior (JSON serializado con model, system, messages, max_tokens). |
| **Transforma** | HTTP POST a `https://api.anthropic.com/v1/messages` con headers `anthropic-version: 2023-06-01` y autenticación por header. |
| **Entrega** | Respuesta JSON de la API Anthropic con array `content[].text`. |
| **Regla de negocio** | Timeout: 30 segundos. Si falla, el flujo se interrumpe (no hay manejo de error configurado aquí). |

---

### Bloque 7 — `Parsear Respuesta Claude`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Code (JavaScript) |
| **Rol** | Extraer el texto de respuesta de Claude y detectar si contiene una acción especial. |
| **Recibe** | Respuesta JSON de la API Anthropic. |
| **Transforma** | Une todos los bloques de tipo `text` del array `content[]`. Busca etiquetas `[COTIZAR: ...]` o `[PAGAR: ...]` con regex. Las elimina del texto visible al usuario (`cleanText`). |
| **Entrega** | `rawText`, `cleanText` (sin etiquetas), `action` (COTIZAR/PAGAR/CHAT), `actionData` (datos parseados de la etiqueta). |
| **Regla de negocio** | La detección es exclusivamente por regex en el texto de Claude. Si Claude no emite la etiqueta correcta, la acción será siempre CHAT. |

**Cómo se detecta si el usuario quiere cotizar, pagar o conversar:**

| Etiqueta en respuesta de Claude | `action` resultante |
|---------------------------------|---------------------|
| `[COTIZAR: nombre=..., rut=..., ...]` | `COTIZAR` |
| `[PAGAR: numero=..., monto=...]` | `PAGAR` |
| Ninguna de las anteriores | `CHAT` |

Claude es instruido a emitir `[COTIZAR: ...]` **solo** cuando tiene todos los datos del cliente (nombre, RUT, dirección, producto, m2, instalación, total). La etiqueta incluye el total pre-calculado que fue inyectado en la instrucción crítica.

**Formato de parsing de la etiqueta `[COTIZAR:]`:**
```js
actionData = {
  nombre: "...",
  rut: "...",
  direccion: "...",
  m2: parseFloat("..."),
  tipo: "...",
  instalacion: true/false,   // "SI" → true
  total: parseInt("...")     // limpia "$", ".", espacios
}
```

---

### Bloque 8 — `Preparar Historial`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Code (JavaScript) |
| **Rol** | Construir el nuevo historial de conversación agregando el turno actual. |
| **Recibe** | Historial previo de Redis, mensaje del usuario, respuesta completa de Claude. |
| **Transforma** | Lee el historial previo, agrega `{role: "user", content: mensaje}` y `{role: "assistant", content: respuesta_completa}`. Limita a los últimos 20 mensajes. |
| **Entrega** | `histValue` (JSON string del nuevo historial), `action`, `actionData`, `cleanText`. |
| **Regla de negocio** | El historial se guarda con la respuesta **completa** de Claude (incluyendo etiquetas `[COTIZAR:]` si las hay), no con el `cleanText`. Esto garantiza que el contexto sea fiel. Límite de 20 turnos para no saturar la API. |

---

### Bloque 9 — `Guardar Historial Redis`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Redis SET |
| **Rol** | Persistir el historial actualizado. |
| **Recibe** | `histKey` (`hist_{uuid}`), `histValue` (JSON string). |
| **Transforma** | Escribe en Redis con TTL de 86.400 segundos (24 horas). |
| **Entrega** | Confirmación de escritura al siguiente nodo. |
| **Regla de negocio** | Cada mensaje reinicia el TTL de 24h para esa sesión. |

**Qué datos se guardan en Redis:**

| Clave Redis | Contenido | TTL |
|-------------|-----------|-----|
| `hist_{uuid}` | Array JSON con últimos 20 pares {role, content} | 24 horas |
| `th:quote:{uuid}` | Objeto JSON con cotización completa | 10 días |
| `th:counter` | Entero incremental para numeración de cotizaciones | Sin expiración |

---

### Bloque 10 — `Switch Acción`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Switch |
| **Rol** | Enrutar el flujo según la acción detectada. |
| **Recibe** | `action` del bloque `Preparar Historial`. |
| **Transforma** | Evalúa el valor de `action`. |
| **Entrega** | Salida 0 si `action == "COTIZAR"`, salida 1 si `action == "PAGAR"`, salida extra (fallback) para `"CHAT"` u otros. |
| **Regla de negocio** | Si Claude no emite ninguna etiqueta, siempre cae en el fallback CHAT. |

---

### Bloque 11 — `Incrementar Contador`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Redis INCR |
| **Rol** | Generar un número secuencial único para la cotización. |
| **Recibe** | (sin datos variables, usa siempre la clave `th:counter`) |
| **Transforma** | Incrementa `th:counter` en Redis en 1 unidad. |
| **Entrega** | El nuevo valor del contador al siguiente nodo. |
| **Regla de negocio** | El contador es global para todas las sesiones. No expira. Genera secuencias como 001, 002, 003... |

---

### Bloque 12 — `Crear Cotización`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Code (JavaScript) |
| **Rol** | Construir el objeto de cotización formal con número, fecha y montos. |
| **Recibe** | `actionData` (de `Parsear Respuesta Claude`), valor del contador (de `Incrementar Contador`). |
| **Transforma** | Genera número `COT-{año}-{seq padded 3}`. Construye objeto `quote`. Formatea el mensaje final para el usuario. |
| **Entrega** | `quote` (objeto completo), `message` (texto formateado con número, m², producto, total, invitación a pagar). |
| **Regla de negocio** | El número de cotización tiene formato `COT-2026-001`. El objeto `quote` usa los datos del `actionData` parseado de la etiqueta de Claude. Si algún campo está vacío, usa valores por defecto (0, "No especificado", false). |

**Dónde se calcula realmente el total:**

> El total **NO se calcula en este nodo ni en Claude**. Se calcula en el nodo `Construir Prompt Claude` (bloque 5) con la fórmula determinística descrita en la sección 5.5. Claude recibe el total pre-calculado y lo incluye verbatim en la etiqueta `[COTIZAR: total=X]`. Este nodo solo lo extrae de esa etiqueta.

---

### Bloque 13 — `Guardar Cotización Redis`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Redis SET |
| **Rol** | Persistir la cotización para referencia futura (pagos, reintentos). |
| **Recibe** | `uuid`, objeto `quote`. |
| **Transforma** | Serializa `quote` a JSON y lo guarda en `th:quote:{uuid}`. |
| **Entrega** | Confirmación de escritura. |
| **Regla de negocio** | TTL de 10 días. Si el usuario vuelve dentro de ese plazo, el sistema recordará su cotización y podrá ofrecerle pagar. |

---

### Bloque 14 — `Respuesta Cotización`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Code (JavaScript) |
| **Rol** | Formatear la respuesta final que verá el usuario al generar su cotización. |
| **Recibe** | `message` y `quote` del nodo `Crear Cotización`. |
| **Transforma** | Re-empaqueta los datos para el nodo de respuesta. `paymentLink` es `null` en esta etapa. |
| **Entrega** | `{ message, quote, paymentLink: null }` |
| **Regla de negocio** | La respuesta incluye número de cotización, m², producto, instalación, total y la instrucción de escribir para pagar. |

---

### Bloque 15 — `Telegram - MsgeCotiza`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Telegram Send Message |
| **Rol** | Notificar al equipo de ventas que se generó una nueva cotización. |
| **Recibe** | Datos de `Crear Cotización`. |
| **Transforma** | Formatea mensaje Markdown. |
| **Entrega** | Mensaje al chat ID `8605918152`. |
| **Regla de negocio** | Se envía **siempre** que se genera una cotización exitosa. |

**Qué datos se notifican por Telegram (cotización):**
- Número de cotización (ej: `COT-2026-001`)
- Producto (tipo de pasto)
- M² con margen técnico
- Si incluye instalación (Sí/No)
- Total en CLP
- Fecha
- UUID del cliente (para rastrear la sesión)

---

### Bloque 16 — `MsjeCotiza` (Gmail)

| Campo | Detalle |
|-------|---------|
| **Tipo** | Gmail Send |
| **Rol** | Enviar resumen de cotización por correo al equipo. |
| **Recibe** | Datos de `Crear Cotización` (via `$json.quote`). |
| **Transforma** | Genera HTML estructurado con tabla de datos. |
| **Entrega** | Email a `aromero.madrid@gmail.com`. |
| **Regla de negocio** | Asunto: "Nueva Cotizacion de Queno". Incluye número, fecha, m², tipo, instalación y total. |

**Qué datos se notifican por Gmail (cotización):**
- Número, Fecha, Superficie (m²), Tipo de pasto, Instalación, Total CLP.

---

### Bloque 17 — `Responder Webhook (Cotizar)`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Respond to Webhook |
| **Rol** | Cerrar la solicitud HTTP y enviar la respuesta JSON al frontend web. |
| **Recibe** | `$json` del nodo anterior en la cadena. |
| **Transforma** | Serializa a JSON con cabeceras CORS. |
| **Entrega** | HTTP 200 JSON al cliente web. |
| **Regla de negocio** | Headers: `Access-Control-Allow-Origin: *`, `Content-Type: application/json`. |

---

### Bloque 18 — `If` (validación para pago)

| Campo | Detalle |
|-------|---------|
| **Tipo** | If |
| **Rol** | Verificar que el monto de la cotización es válido antes de crear la preferencia de pago. |
| **Recibe** | `actionData.monto` del flujo de PAGAR. |
| **Transforma** | Evalúa si `monto > 0`. |
| **Entrega** | Salida TRUE → `Llamar MercadoPago`. Salida FALSE → `Respuesta Sin Cotización1`. |
| **Regla de negocio** | Esta es la única validación matemática del monto. No verifica coherencia con el producto ni el m². |

**Cómo se valida que el monto sea correcto antes de crear la cotización:**  
> **Actualmente no existe una validación matemática real.** El único control es que `monto > 0`. No se recalcula el total para verificar que el valor parseado de la etiqueta `[COTIZAR:]` coincida con `m2 × precio × margen`. Esta es una brecha identificada (ver sección 4).

---

### Bloque 19 — `Llamar MercadoPago`

| Campo | Detalle |
|-------|---------|
| **Tipo** | HTTP Request POST |
| **Rol** | Crear una preferencia de pago en MercadoPago. |
| **Recibe** | (actualmente usa datos hardcodeados de prueba, no los datos reales de la cotización) |
| **Transforma** | POST a `https://api.mercadopago.com/checkout/preferences`. |
| **Entrega** | URL de checkout (`init_point` o `sandbox_init_point`). |
| **Regla de negocio** | **ATENCIÓN:** Los datos del item (precio, nombre, moneda) están hardcodeados como valores de prueba (`unit_price: 3500`, `currency_id: "ARS"`). No usa los datos reales del cliente ni el total de la cotización. Timeout: 15 segundos. |

---

### Bloque 20 — `Respuesta Pago`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Code (JavaScript) |
| **Rol** | Formatear la respuesta con el link de pago generado. |
| **Recibe** | Respuesta de MercadoPago, datos del `Parsear Respuesta Claude`. |
| **Transforma** | Extrae `init_point` o `sandbox_init_point`. Genera mensaje con link. |
| **Entrega** | `{ message, quote, paymentLink }` |
| **Regla de negocio** | Si MercadoPago no devuelve link, muestra mensaje de error y sugiere contacto directo. |

---

### Bloque 21 — Notificaciones de Pago (Telegram + Gmail)

**`Send a text message1` (Telegram):**

| Dato notificado | Origen |
|----------------|--------|
| Número de cotización | `actionData.numero` |
| Monto | `actionData.monto` |
| Link de pago | `paymentLink` |
| Fecha/hora | `new Date()` en el momento de ejecución |

**`MsjeVenta1` (Gmail):**

Envía HTML completo al mismo correo con: número de orden, producto, m², instalación, total pagado, y detalle de próximos pasos.

---

### Bloque 22 — `Respuesta Simple`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Code (JavaScript) |
| **Rol** | Respuesta para mensajes de conversación general (sin cotización ni pago). |
| **Recibe** | `cleanText` del flujo principal. |
| **Transforma** | Empaqueta en formato estándar. |
| **Entrega** | `{ message: cleanText, quote: null, paymentLink: null }` |
| **Regla de negocio** | Usado para toda la conversación previa a cotizar: saludo, consultas, elección de producto, ingreso de m², confirmación de instalación. |

---

### Bloque 23 — `Respuesta Sin Cotización1`

| Campo | Detalle |
|-------|---------|
| **Tipo** | Code (JavaScript) |
| **Rol** | Manejo del caso en que el usuario intenta pagar sin cotización válida. |
| **Recibe** | Flujo de PAGAR con monto = 0. |
| **Entrega** | `{ message: "Revisar o generar cotización previa", quote: null, paymentLink: null }` |
| **Regla de negocio** | Mensaje genérico. No indica al usuario cómo retomar el proceso de cotización. |

---

## 3. Preguntas específicas de negocio y técnicas

### ¿Cómo se recibe el mensaje del usuario desde la web?

La web envía `POST /chat` con cuerpo JSON `{ sessionId: "...", message: "..." }`. El `sessionId` es la clave que une todos los mensajes de un mismo usuario en Redis. Si la web no envía `sessionId`, se genera uno nuevo por petición, lo que **rompe el historial** (cada mensaje sería una conversación nueva).

---

### ¿Qué información se consulta en Redis y para qué se usa?

| Clave | Para qué se usa |
|-------|-----------------|
| `hist_{uuid}` | Mantener contexto conversacional: recuperar nombre, RUT, dirección, producto y m² ya informados |
| `th:quote:{uuid}` | Saber si el usuario ya tiene cotización y ofrecerle pagar directamente |
| `th:counter` | Numerar cotizaciones secuencialmente (COT-2026-001, 002...) |

---

### ¿Qué contexto se le entrega a Claude antes de responder?

1. **System prompt** con identidad, catálogo, flujo numerado, reglas de respuesta.
2. **Instrucción crítica** (si aplica): texto exacto que Claude debe responder, con totales pre-calculados ya incluidos.
3. **Historial completo** como array de mensajes `{ role, content }`.
4. **Mensaje actual** del usuario.
5. **Contexto de cotización existente** si ya tiene una (en el system prompt).

---

### ¿Qué reglas exactas se enviaron a Claude para calcular metraje?

Claude **no calcula el metraje**. Solo recibe esta indicación genérica:

> `"Siempre aplicar 10% margen tecnico sobre m2 solicitados."`

El cálculo real lo ejecuta el sistema en `Construir Prompt Claude`:
```
m2ConMargen = Math.ceil(m2Solicitados × 1.10)
subtotalPasto = m2ConMargen × precioPorM²
subtotalInstalacion = m2ConMargen × 4.500  (si instalación = SI)
total = subtotalPasto + subtotalInstalacion
```

Claude recibe estos valores ya calculados en la instrucción crítica y los copia textualmente en la etiqueta `[COTIZAR:]`.

---

### ¿Cómo interpreta Claude largo, ancho, metros cuadrados y margen de corte?

**Claude no recibe instrucciones para interpretar largo ni ancho.** El sistema espera recibir el m² ya como un único número. El regex en el código solo procesa:

- `20` → 20 m²
- `20m2` → 20 m²
- `20,5 metros` → 20,5 m²

**No procesa:** `5 x 4`, `5 por 4`, `largo: 5, ancho: 4`. En esos casos el sistema no detecta m², no genera `instruccionInmediata` y Claude queda a su libre interpretación según las reglas generales del FLUJO, lo que puede resultar en comportamiento inconsistente.

---

### ¿Cómo se detecta si el usuario quiere cotizar, pagar o solo conversar?

- **COTIZAR:** Claude emite `[COTIZAR: nombre=..., rut=..., ...]` — solo ocurre cuando el nodo `Construir Prompt Claude` detectó que estamos en paso "tras dirección" y genera la instrucción crítica con esa etiqueta ya escrita que Claude debe copiar.
- **PAGAR:** Claude emite `[PAGAR: numero=..., monto=...]` — se activa cuando el system prompt incluye `quoteContext` con una cotización existente y el usuario expresa intención de pagar.
- **CHAT:** Cualquier otro mensaje (sin etiquetas). Es el estado por defecto.

---

### ¿Dónde se calcula realmente el total?

**En el nodo `Construir Prompt Claude`**, en JavaScript del servidor n8n, antes de llamar a Claude. Claude no realiza aritmética; recibe el resultado ya calculado. Sin embargo, existe un riesgo: si Claude reformatea el número en la etiqueta (ej: agrega separadores de miles), el parser `limpiarNumero` podría fallar silenciosamente y devolver `0`.

---

### ¿Cómo se valida que el monto generado sea correcto antes de crear la cotización?

**No existe validación matemática.** El único control es `If (monto > 0)` antes de llamar a MercadoPago. No hay verificación de que `total == m2 × precio × 1.10 ± instalación`. Esta validación está ausente y es un riesgo de negocio.

---

### ¿Qué datos se guardan en Redis?

| Clave | Tipo | Campos | TTL |
|-------|------|--------|-----|
| `hist_{uuid}` | Array JSON | `[{ role: "user"\|"assistant", content: "..." }, ...]` (máx 20) | 24 h |
| `th:quote:{uuid}` | Objeto JSON | `{ numero, uuid, m2, tipo, instalacion, total, fecha, timestamp }` | 10 días |
| `th:counter` | Integer | Valor numérico incremental | Sin TTL |

---

### ¿Qué datos se notifican por Telegram y Gmail?

**Al generar cotización:**

| Canal | Datos enviados |
|-------|---------------|
| Telegram | Número cotización, producto, m², instalación, total CLP, fecha, UUID |
| Gmail | Número, fecha, m², tipo pasto, instalación, total CLP |

**Al iniciar pago:**

| Canal | Datos enviados |
|-------|---------------|
| Telegram | Número cotización, monto, link de pago MercadoPago, fecha/hora |
| Gmail | Número, producto, m², instalación, total, instrucciones de próximos pasos |

---

### ¿Qué ocurre si el usuario entrega medidas incompletas, ambiguas o mal expresadas?

| Caso | Comportamiento actual |
|------|-----------------------|
| `"5 x 3"` / `"5 por 3"` | Regex no detecta m². El sistema no genera instrucción crítica. Claude guía según reglas generales pero sin cálculo determinístico. Resultado impredecible. |
| `"tengo unos 20 metros"` | Regex no hace match (texto no es solo número). Mismo problema anterior. |
| Solo `"largo: 5"` sin ancho | No se detecta ni largo ni ancho. El sistema no sabe calcular. |
| Número muy alto ej. `5000` | Se acepta sin validación. Podría generar cotizaciones incoherentes. |
| Número decimales con punto ej. `20.5` | El regex acepta punto y coma. OK. |
| Usuario escribe solo `20` cuando el sistema pide el RUT | Si `estadoEnDatos` es `true`, el regex se desactiva. Correcto. |
| Medidas en distintos turnos (primero largo, luego ancho) | El sistema no tiene memoria de dimensiones parciales. No suma ni combina. |

**No existe lógica de aclaración para medidas ambiguas.** Claude podría pedir que reformule, pero no está explícitamente instruido para ello.

---

## 4. Problemas identificados y recomendaciones

### Problema 1 — No se soportan dimensiones largo × ancho

**Síntoma:** El usuario dice "tengo un jardín de 5 por 8 metros" y el sistema no calcula.  
**Causa:** El regex solo acepta un único número, no expresiones multiplicativas.  
**Recomendación:** En el nodo `Construir Prompt Claude`, agregar un regex secundario para detectar `5x8`, `5 × 8`, `5 por 8` y calcular `m2 = largo × ancho` antes del cálculo principal.

```js
// Regex sugerido
const regexDimensiones = /(\d+([.,]\d+)?)\s*(x|×|por)\s*(\d+([.,]\d+)?)/i;
const matchDim = message.match(regexDimensiones);
if (matchDim) {
  const largo = parseFloat(matchDim[1].replace(',', '.'));
  const ancho = parseFloat(matchDim[4].replace(',', '.'));
  m2Valor = largo * ancho;
}
```

---

### Problema 2 — No hay validación matemática posterior al parseo de Claude

**Síntoma:** Claude podría formatear el total con puntos de miles (`$11.550`) y el parser lo limpiaría a `11550`... o podría modificar el número y el sistema lo aceptaría sin verificar.  
**Recomendación:** En el nodo `Crear Cotización`, recalcular el total internamente y compararlo con el parseado:

```js
// Recalcular para validar
const preciosPorM2 = { 'Pasto Basico (20mm)': 8500, 'Pasto Premium (35mm)': 15000, 'Pasto Deportivo (25mm)': 12000 };
const precioProducto = preciosPorM2[actionData.tipo] || 0;
const totalEsperado = actionData.m2 * precioProducto + (actionData.instalacion ? actionData.m2 * 4500 : 0);
// Usar totalEsperado en vez de actionData.total
```

---

### Problema 3 — MercadoPago usa datos hardcodeados

**Síntoma:** El link de pago tiene precio y producto de prueba, no los datos reales.  
**Causa:** El nodo `Llamar MercadoPago` tiene datos fijos en su JSON body.  
**Recomendación:** Reemplazar los valores hardcodeados con referencias a la cotización real (`$json.quote.total`, `$json.quote.tipo`, datos del cliente).

---

### Problema 4 — Redis podría no estar guardando correctamente el contexto

**Síntoma:** Claude vuelve a preguntar datos que el usuario ya entregó.  
**Causa probable:** Si la web no envía siempre el mismo `sessionId`, se crea una sesión nueva en cada mensaje y el historial empieza vacío.  
**Verificación:** Confirmar en los logs de n8n que el `uuid` sea el mismo entre mensajes consecutivos de un mismo usuario.

---

### Problema 5 — El flujo no detecta correctamente cuándo la cotización está completa

**Síntoma:** A veces no se genera la etiqueta `[COTIZAR:]`.  
**Causa:** La instrucción crítica de generar la etiqueta solo se activa si `estadoPidiendoDireccion` es `true` en el momento en que el usuario responde la dirección. Si el historial está desincronizado o incompleto, `estadoPidiendoDireccion` puede ser `false` y la instrucción no se genera.  
**Recomendación:** Agregar una lógica alternativa: si `nombreCapturado`, `rutCapturado`, `direccionCapturada`, `productoNombre` y `m2Final > 0` están todos presentes, generar la instrucción crítica de cotización independientemente del estado del último mensaje.

---

### Resumen de la fórmula de cálculo (correcta, ya implementada)

$$m^2_{margen} = \lceil m^2_{solicitados} \times 1{,}10 \rceil$$

$$subtotal_{pasto} = m^2_{margen} \times precio_{producto}$$

$$subtotal_{inst} = \begin{cases} m^2_{margen} \times 4500 & \text{si instalación = SI} \\ 0 & \text{si instalación = NO} \end{cases}$$

$$\text{Total} = subtotal_{pasto} + subtotal_{inst}$$

Esta fórmula **ya está correctamente implementada** en el nodo `Construir Prompt Claude`. El principal problema no es la fórmula sino que el sistema no detecta medidas expresadas en formato largo × ancho.
