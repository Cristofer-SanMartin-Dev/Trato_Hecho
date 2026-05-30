# VERDAD DEL PROYECTO — Extraída del código fuente
# Generado automáticamente por auditoría de código
# Fecha: 2026-05-21
# Este archivo es la fuente de verdad para toda la documentación

---

## INFRAESTRUCTURA REAL

### n8n (orquestador)
- Hosting: Railway
- URL de producción: https://main-production-38ed.up.railway.app
- Despliegue local: `docker run` con imagen `n8nio/n8n:latest`
- Puerto local: 5678
- Comando docker local (del README.md):
  ```
  docker run -d --name trato_hecho_n8n --restart unless-stopped \
    -p 127.0.0.1:5678:5678 \
    -v trato_hecho_n8n_data:/home/node/.n8n \
    n8nio/n8n:latest
  ```

### Frontend
- Tipo: HTML/JavaScript vanilla + Tailwind CSS (NO es React ni Vue)
- Hosting: Vercel
- Archivos clave: index.html, chatbot.js, config.js, calculadora.html
- Configuración Vercel: Producto/config/vercel.json (outputDirectory: ".", no buildCommand)
- Requiere Node 18+ solo para servir localmente con `npx serve`

### Base de datos
- Tipo: Supabase (cloud, PostgreSQL gestionado)
- URL del proyecto Supabase: https://enpzxntzphvezopbxbtx.supabase.co
- NO hay PostgreSQL local ni Redis en el sistema actual
- Tablas en Supabase:
  - `cotizaciones` — cotizaciones formales
  - `historial` — historial conversacional por sesión

### Docker Compose
- NO existe docker-compose.yml en el repositorio
- n8n se despliega con `docker run` individual (ver README.md)
- No hay servicios de Redis ni PostgreSQL local configurados

---

## ENDPOINTS REALES (de Producto/config/config.js y workflow AI Agent v2)

- URL webhook producción: `https://main-production-38ed.up.railway.app/webhook/chat-v2`
- URL webhook local: `http://localhost:5678/webhook/chat-v2`
- Path del webhook (en n8n): `/webhook/chat-v2`
- Workflow activo en producción: `Trato Hecho - AI Agent v2.json`
- Método HTTP: POST
- Headers requeridos: `Content-Type: application/json`
- Campos del body:
  ```json
  {
    "message": "texto del usuario (requerido)",
    "sessionId": "identificador único de sesión (generado por chatbot.js)"
  }
  ```
- Respuesta JSON del webhook:
  ```json
  {
    "message": "texto de respuesta",
    "quote": null | { objeto cotización },
    "paymentLink": null | "URL de MercadoPago"
  }
  ```

### Nota sobre workflows:
- `workflow_current.json` → path `/webhook/chat`, modelo `claude-sonnet-4-5` (versión anterior)
- `Trato Hecho - AI Agent v2.json` → path `/webhook/chat-v2`, modelo `claude-sonnet-4-6` (PRODUCCIÓN)
- El archivo `config.js` confirma que producción usa `/webhook/chat-v2`

---

## MODELO DE IA REAL (de Trato Hecho - AI Agent v2.json)

- Nombre del modelo: `claude-sonnet-4-6`
- max_tokens: 1024
- Versión API Anthropic: `2023-06-01` (header `anthropic-version`)
- Endpoint: `https://api.anthropic.com/v1/messages`
- Timeout: 30 segundos
- Autenticación: Bearer token (httpHeaderAuth en n8n)

---

## BASE DE DATOS REAL (Supabase)

### Tabla `cotizaciones`
Campos inferidos del objeto `quote` en el nodo "Crear Cotización":
- `numero` — VARCHAR, formato `COT-YYYY-XXXXX` donde XXXXX son los últimos 5 dígitos del timestamp
- `session_id` — VARCHAR, identificador de sesión del cliente
- `nombre` — VARCHAR, nombre completo del cliente
- `rut` — VARCHAR, RUT del cliente (formato: 12.345.678-9)
- `direccion` — VARCHAR, dirección de instalación
- `producto` — VARCHAR, nombre del producto (Luxury Emerald, Soft Touch, etc.)
- `m2` — NUMERIC, metros cuadrados solicitados (sin margen)
- `instalacion` — BOOLEAN, si incluye servicio de instalación
- `total` — INTEGER, total en CLP (calculado server-side)
- `estado` — VARCHAR, valor inicial: `'pendiente'`
- `created_at` — TIMESTAMP, generado automáticamente por Supabase

### Tabla `historial`
- `session_id` — VARCHAR, PK o UNIQUE, identifica la sesión
- `messages` — JSONB, array de `[{ role: "user"|"assistant", content: "texto" }]`
- `updated_at` — TIMESTAMP ISO

### Número de cotización — formato REAL:
```javascript
const year = new Date().getFullYear();
const seq  = String(Date.now()).slice(-5);  // últimos 5 dígitos del timestamp
const numero = 'COT-' + year + '-' + seq;
// Ejemplo: COT-2026-52348
```
**IMPORTANTE:** No es secuencial. No usa contador Redis. Usa timestamp para unicidad.

---

## CATÁLOGO DE PRODUCTOS REAL (de Trato Hecho - AI Agent v2.json)

### Productos residenciales:
| Producto | Grosor | Precio/m² |
|---|---|---|
| Luxury Emerald | 40mm | $28.500 CLP |
| Soft Touch | 30mm | $22.900 CLP |
| Pet-Friendly Turf | 35mm | $26.000 CLP |

### Productos deportivos (precio a cotizar):
| Tipo | Descripción |
|---|---|
| Pasto Deportivo Fútbol 7 | Cancha de fútbol 7 |
| Pasto Deportivo Fútbol 11 | Cancha de fútbol 11 |
| Pasto Tenis & Pádel | Cancha de tenis o pádel |

### Instalación:
- Precio instalación: **+$4.500/m²** (solo productos residenciales)
- No aplica para deportivos

### Fórmula de cálculo (server-side en n8n):
```javascript
m2Margen      = Math.ceil(m2Final * 1.10)          // +10% margen técnico
subtotalPasto = m2Margen * precioPorM2
subtotalInst  = instalacion === true ? m2Margen * 4500 : 0
totalFinal    = subtotalPasto + subtotalInst
```

---

## COMPONENTES FRONTEND REALES (de Producto/frontend/)

- Página principal: `index.html`
- Chat widget: implementado inline en `index.html` + lógica en `chatbot.js`
- Hook/lógica de chat: `chatbot.js`
- Configuración URL webhook: `config.js`
- Calculadora de m²: `calculadora.html`
- Página de jardines: `jardines.html`
- Página de pasto deportivo: `pasto-deportivo.html`
- Página de contacto: `contacto.html`
- Página de insumos: `insumos.html`
- Configuración Vercel: `Producto/config/vercel.json`

### Cómo se almacena el sessionId:
```javascript
// Almacenamiento primario: sessionStorage
// Almacenamiento secundario: localStorage (fallback entre pestañas)
sessionId = sessionStorage.getItem('chatSessionId')
         || localStorage.getItem('chatSessionId')
         || "sess_" + Math.random().toString(36).substr(2, 9);
sessionStorage.setItem('chatSessionId', sessionId);
localStorage.setItem('chatSessionId', sessionId);
```

### Historial del chat:
- Historial de mensajes DOM: `sessionStorage('chatHistory')` (HTML serializado)
- Historial estructurado para n8n: `sessionStorage('chatHistoryData')` (JSON, max 40 entradas)

---

## FLUJO DE ACCIONES (de workflow)

El agente detecta 3 acciones por etiquetas en la respuesta de Claude:

| Etiqueta en respuesta Claude | Acción | Ruta n8n |
|---|---|---|
| `[COTIZAR: nombre=X, rut=X, ...]` | COTIZAR | Guardar Supabase → Telegram → Gmail → Webhook |
| `[PAGAR: numero=X, monto=X]` | PAGAR | MercadoPago → Telegram → Gmail → Webhook |
| Sin etiqueta | CHAT | Respuesta directa → Webhook |

---

## NOTIFICACIONES REALES

### Telegram:
- Chat ID: `8605918152`
- Se notifica: al generar cotización (número, producto, m², instalación, total, fecha, UUID)
- Se notifica: al iniciar pago (número cotización, monto, link de pago, fecha)

### Gmail:
- Destinatario: `aromero.madrid@gmail.com`
- Asunto cotización: "Nueva Cotizacion de Queno"
- Asunto pago: notificación con datos del pago

---

## MERCADOPAGO (de workflow_current.json)

**ATENCIÓN:** En el archivo `workflow_current.json`, el nodo "Llamar MercadoPago" tiene datos hardcodeados de prueba:
```json
{ "title": "Producto de Prueba", "unit_price": 3500, "currency_id": "ARS" }
```
En el archivo `Trato Hecho - AI Agent v2.json` (PRODUCCIÓN) se usan datos reales de la cotización:
```javascript
{ title: 'Césped Sintético ARM — ' + cotizacion.producto,
  currency_id: 'CLP',
  unit_price: cotizacion.total }
```
- Endpoint MP: `https://api.mercadopago.com/checkout/preferences`
- Timeout: 15 segundos
- Moneda producción: CLP
- Moneda en workflow_current (prueba): ARS — **DATO INCORRECTO EN ESA VERSIÓN**

---

## STACK TECNOLÓGICO REAL

| Capa | Tecnología | Detalles | Hosting |
|---|---|---|---|
| Frontend | HTML/CSS/JS vanilla | Tailwind CSS via CDN, NO React | Vercel |
| Chat JS | JavaScript ES6+ | chatbot.js + config.js | Vercel |
| Orquestador | n8n | Docker (n8nio/n8n:latest) | Railway |
| IA | Claude Sonnet 4.6 | claude-sonnet-4-6, max_tokens=1024 | Anthropic API |
| Base de datos | Supabase | PostgreSQL gestionado en cloud | Supabase.co |
| Pagos | MercadoPago | Checkout API, CLP | MercadoPago |
| Notificaciones | Telegram Bot | Chat ID: 8605918152 | Telegram |
| Email | Gmail | Gmail OAuth2 | Google |

---

## VARIABLES DE ENTORNO REALES (de Producto/config/.env.example)

```env
N8N_USER=admin
N8N_PASSWORD=cambia_esto_123
WEBHOOK_URL=http://localhost:5678/
N8N_PROTOCOL=http
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXX
MERCADOPAGO_ACCESS_TOKEN=TEST-XXXXXXXXXXXXXXXXXXXX
FRONTEND_URL=http://localhost:3000
```
**Nota:** No hay variables de entorno para Redis, PostgreSQL local, ni Supabase en el .env.example.
La Supabase API key está hardcodeada en el workflow JSON (anon key).

---

## HOSTING Y DESPLIEGUE REAL

- Frontend: Vercel (HTML estático, sin build step)
- Backend/n8n: Railway (Docker container con `n8nio/n8n:latest`)
- Base de datos: Supabase (cloud, https://enpzxntzphvezopbxbtx.supabase.co)
- Redis: NO se usa Redis en el sistema actual
- MercadoPago: Cloud (API externa)
- Telegram: Cloud (Bot API)
- Gmail: Cloud (OAuth2 desde n8n)

---

## ARCHIVOS DE CÓDIGO AUDITADOS

1. `Producto/config/config.js` — URL del webhook de producción
2. `Producto/frontend/chatbot.js` — Lógica del chat widget
3. `Producto/config/vercel.json` — Configuración de Vercel
4. `Producto/config/.env.example` — Variables de entorno
5. `Producto/n8n/workflow_current.json` — Workflow n8n (versión anterior, path /chat)
6. `Producto/n8n/Trato Hecho - AI Agent v2.json` — Workflow n8n PRODUCCIÓN (path /chat-v2)
7. `Producto/n8n/DOCUMENTACION_FLUJO.md` — Documentación del flujo (parcialmente desactualizada)
8. `Producto/frontend/index.html` — Página principal
9. `README.md` — Manual de instalación

---

## INCONSISTENCIAS DETECTADAS

### 1. CRÍTICA — Modelo de Claude (DOCUMENTACION_FLUJO.md vs código real)
- `DOCUMENTACION_FLUJO.md` dice: `claude-sonnet-5-6`
- Workflow producción dice: `claude-sonnet-4-6`
- **La verdad es: `claude-sonnet-4-6`**

### 2. CRÍTICA — Catálogo de productos (DOCUMENTACION_FLUJO.md vs código real)
- `DOCUMENTACION_FLUJO.md` describe:
  - Pasto Basico (20mm): $8.500/m²
  - Pasto Premium (35mm): $15.000/m²
  - Pasto Deportivo (25mm): $12.000/m²
- El código real (workflow AI Agent v2) usa:
  - Luxury Emerald (40mm): $28.500/m²
  - Soft Touch (30mm): $22.900/m²
  - Pet-Friendly Turf (35mm): $26.000/m²
  - Deportivos: precio a cotizar (sin precio fijo)
- **La verdad es el catálogo del código: Luxury/Soft Touch/Pet-Friendly**

### 3. CRÍTICA — Base de datos (Redis vs Supabase)
- `DOCUMENTACION_FLUJO.md` describe Redis con claves `hist_{uuid}`, `th:quote:{uuid}`, `th:counter`
- El código real usa **Supabase REST API** (tablas `historial` y `cotizaciones`)
- **La verdad es: Supabase, sin Redis**

### 4. ALTA — Formato número de cotización
- Documentación describe: `COT-2026-001` (secuencial, 3 dígitos, contador Redis)
- Código real genera: `COT-2026-52348` (últimos 5 dígitos de timestamp, NO secuencial)
- **La verdad es: formato `COT-YYYY-XXXXX` basado en timestamp**

### 5. ALTA — Tipo de frontend (React vs HTML vanilla)
- Algunos documentos pueden decir "React"
- El código real es HTML/JavaScript vanilla con Tailwind CSS
- **La verdad es: NO hay React, es HTML estático**

### 6. MEDIA — Webhook path (/chat vs /chat-v2)
- `workflow_current.json` usa path `/webhook/chat`
- `config.js` (producción) y `AI Agent v2.json` usan `/webhook/chat-v2`
- **La verdad es: producción usa `/webhook/chat-v2`**

### 7. MEDIA — Diagrama `Trato_Hecho_Redis.drawio` existe pero Redis ya no se usa
- El diagrama describe arquitectura Redis que ya fue reemplazada por Supabase
- El diagrama debería actualizarse o reemplazarse

### 8. BAJA — MercadoPago: moneda ARS vs CLP
- `workflow_current.json` tiene datos hardcodeados con `currency_id: "ARS"` (prueba)
- `AI Agent v2.json` (producción) usa `currency_id: "CLP"` con datos reales
- **La verdad de producción es: CLP con datos reales de la cotización**
