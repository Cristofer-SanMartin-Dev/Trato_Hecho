# GUÍA COMPLETA — Claude Code · Evaluación Parcial 2
## Trato Hecho · DuocUC · Entrega 30 mayo 2026
## PRINCIPIO FUNDAMENTAL: El código manda, la documentación sirve al código

---

## ⚠ IMPORTANTE — LEE ESTO ANTES DE EMPEZAR

**La documentación NO define el proyecto. El código sí.**

El trabajo de Claude Code tiene DOS etapas en este orden:
1. Leer el código real → extraer la verdad del proyecto
2. Adaptar/corregir la documentación para que refleje esa verdad

Si el código dice `/webhook/chat-v2` y un documento dice `/webhook/chat`, 
el documento está mal, no el código. Claude Code corrige el documento.

---

## PASO 0 — LO QUE DEBES HACER TÚ ANTES DE ABRIR CLAUDE CODE

### 0.1 Crear la rama de trabajo

```bash
git checkout main
git pull origin main
git checkout -b docs/ep2-evaluacion-parcial-2
git branch
# Debe mostrar: * docs/ep2-evaluacion-parcial-2
```

### 0.2 Crear la estructura de carpetas requerida por DuocUC

El profesor exige EXACTAMENTE estas carpetas en el repositorio:

```bash
mkdir -p Documentacion/word
mkdir -p Documentacion/mockups
mkdir -p Documentacion/diagramas
mkdir -p Documentacion/historias-usuario
mkdir -p Producto
mkdir -p Gestion/planificacion
mkdir -p Gestion/riesgos
```

### 0.3 Copiar los archivos ya generados

```bash
# Documentos Word
cp 01_Documentacion_Tecnica_Completa.docx    Documentacion/word/
cp 02_Manual_Instalacion.docx                Documentacion/word/
cp 03_Manual_Usuario.docx                    Documentacion/word/
cp 04_Documentacion_Flujo_N8N.docx           Documentacion/word/
cp 05_Especificacion_Requerimientos_SRS.docx Documentacion/word/
cp 06_Plan_Pruebas.docx                      Documentacion/word/
cp 07_Informe_Cierre.docx                    Documentacion/word/

# Diagramas draw.io
cp Trato_Hecho_Flujo_N8N.drawio      Documentacion/diagramas/
cp Trato_Hecho_Arquitectura.drawio   Documentacion/diagramas/
cp Trato_Hecho_ERD.drawio            Documentacion/diagramas/
cp Trato_Hecho_Secuencia.drawio      Documentacion/diagramas/
cp Trato_Hecho_Flujo_UX.drawio       Documentacion/diagramas/
cp Trato_Hecho_Redis.drawio          Documentacion/diagramas/
cp Trato_Hecho_Mapa_Diagramas.drawio Documentacion/diagramas/

# Historias de usuario
cp Historias_Usuario_Trato_Hecho.xlsx Documentacion/historias-usuario/

# Gestión
cp Carta_Gantt_Trato_Hecho.xlsx      Gestion/planificacion/
cp matriz_riesgo_trato_hecho.xlsx    Gestion/riesgos/
```

### 0.4 Copiar el código fuente a Producto/

```bash
# Ajusta las rutas a donde tengas el código real
cp -r src/               Producto/frontend/
cp -r n8n/               Producto/n8n/
cp docker-compose.yml    Producto/
cp package.json          Producto/
```

### 0.5 Abrir Claude Code en la raíz del repositorio

```bash
claude
```

---

## PASO 1 — PRIMER PROMPT: Extracción de la verdad del proyecto

**Propósito:** Que Claude Code lea el código real y genere el documento de verdad
que todos los demás prompts usarán como referencia.

---

```
Eres el auditor técnico del proyecto "Trato Hecho" para la Evaluación Parcial 2
de DuocUC (TPY1101). Tu principio de trabajo es: EL CÓDIGO ES LA FUENTE DE VERDAD.
La documentación existe para describir lo que el código hace, no al revés.

## TAREA: Leer el código y extraer la verdad del proyecto

### PASO 1.1 — Lee el código fuente del proyecto

Lee todos los archivos en Producto/ con este orden de prioridad:

1. Producto/n8n/ — el workflow JSON del agente (es el núcleo del sistema)
   - Busca el archivo workflow*.json o Trato_Hecho*.json
   - Extrae: URL exacta del webhook, nombre de nodos, claves Redis reales,
     nombre de tabla PostgreSQL, modelo de Claude, estructura de la respuesta JSON

2. Producto/frontend/src/ — el código React
   - Busca config.js o similar → extrae la URL real del webhook configurada
   - Busca useChat.js o similar → extrae cómo se maneja el sessionId/uuid
   - Busca los componentes: ChatWidget, ChatWindow, QuoteCard, Calculator
   - Confirma si usan useState, Redux u otro manejador de estado

3. Producto/docker-compose.yml — la infraestructura real
   - Extrae: puertos reales, nombres de servicios, versiones de imágenes Docker
   - Confirma: ¿es PostgreSQL o Supabase? ¿Qué versión de Redis?

4. Producto/package.json — dependencias reales
   - Extrae: versión real de React, librerías instaladas realmente

5. Producto/n8n/*.py — scripts de despliegue si existen
   - Extrae: URL real de n8n, estructura del workflow

### PASO 1.2 — Genera el archivo VERDAD_PROYECTO.md

Crea Documentacion/VERDAD_PROYECTO.md con estos datos extraídos del código:

```markdown
# VERDAD DEL PROYECTO — Extraída del código fuente
# Generado automáticamente por auditoría de código
# Fecha: [fecha de hoy]
# Este archivo es la fuente de verdad para toda la documentación

## INFRAESTRUCTURA REAL (de docker-compose.yml)
- Frontend puerto: [extraído]
- n8n puerto: [extraído]
- PostgreSQL puerto y versión: [extraído]
- Redis puerto y versión: [extraído]
- Nombre de servicios Docker: [extraído]

## ENDPOINTS REALES (de workflow JSON y config.js)
- URL webhook: [URL exacta del código]
- Path del webhook: [path exacto]
- Método HTTP: [GET/POST]
- Campos del body: [campos reales]

## MODELO DE IA REAL (de workflow JSON)
- Nombre del modelo: [modelo exacto del código]
- max_tokens: [valor real]
- Versión API Anthropic: [header anthropic-version real]

## CLAVES REDIS REALES (de workflow JSON)
- Clave historial: [clave exacta]
- TTL historial: [segundos exactos]
- Clave cotización: [clave exacta]
- TTL cotización: [segundos exactos]
- Clave contador: [clave exacta]

## TABLA POSTGRESQL REAL (de workflow JSON o scripts SQL)
- Nombre de tabla: [nombre exacto]
- Campos reales: [lista de campos reales]
- Nombre del campo número de cotización: [nombre exacto]
- Formato del número: [formato exacto, ej: COT-2026-001]

## COMPONENTES FRONTEND REALES (de src/)
- Archivo del widget de chat: [nombre real]
- Archivo del hook de chat: [nombre real]
- Archivo de configuración: [nombre real]
- Cómo se almacena el sessionId: [localStorage/sessionStorage/state]

## HOSTING Y DESPLIEGUE REAL (de docker-compose y README existente)
- Frontend: [Vercel/Netlify/otro]
- Backend/n8n: [Railway/Render/otro — CONFIRMAR cuál se usa realmente]
- Base de datos: [Railway managed/Supabase/otro]
- Redis: [Railway Redis/Upstash/otro]

## STACK TECNOLÓGICO REAL (de package.json)
- Versión React: [real]
- Versión Node: [real]
- Librerías principales instaladas: [lista real]

## INCONSISTENCIAS DETECTADAS
Lista de datos que difieren entre documentos:
- [doc A] dice X, [doc B] dice Y, el código dice Z → la verdad es Z
```

### PASO 1.3 — Reporta el resultado

Al terminar muestra:
- Cuántos archivos de código leíste
- Las 3 inconsistencias más críticas encontradas entre documentación y código
- Confirma: "VERDAD_PROYECTO.md generado con [N] datos extraídos del código"

Si algún archivo de código no existe o no puedes leerlo, indícalo claramente.
No inventes datos. Si no encuentras algo en el código, escribe "NO ENCONTRADO EN CÓDIGO".
```

---

## PASO 2 — SEGUNDO PROMPT: Auditoría y corrección de documentación

**Propósito:** Comparar cada documento Word con VERDAD_PROYECTO.md
y corregir lo que no refleje el código real.

---

```
Usa el archivo Documentacion/VERDAD_PROYECTO.md como única fuente de verdad.

## TAREA: Auditar y corregir los 7 documentos Word

Para cada documento en Documentacion/word/ ejecuta este proceso:

### PROCESO POR DOCUMENTO:

1. Lee el documento
2. Compara CADA dato técnico contra VERDAD_PROYECTO.md
3. Anota las discrepancias encontradas
4. Aplica las correcciones necesarias

### DATOS A VERIFICAR EN CADA DOCUMENTO:

☐ URL/path del webhook (¿coincide con el código?)
☐ Nombre del modelo de Claude (¿es el modelo real del workflow?)
☐ Claves Redis con TTL (¿son las claves reales?)
☐ Nombre de la tabla PostgreSQL (¿es el nombre real?)
☐ Formato número de cotización (¿es el formato real del código?)
☐ Hosting del backend (¿Railway o Render? ¿cuál usa el proyecto realmente?)
☐ Versión de React (¿coincide con package.json?)
☐ Puertos de los servicios (¿coinciden con docker-compose.yml?)
☐ Campos del body del webhook (¿son los campos reales que envía el frontend?)
☐ Componentes React (¿los nombres coinciden con los archivos reales en src/?)

### CRITERIO DE CORRECCIÓN:

Si el documento dice X y el código dice Y → corrige el documento para que diga Y.
Nunca cambies el código para que coincida con la documentación.
Si un dato no está en el código (NO ENCONTRADO), déjalo como está en el documento
y márcalo con [PENDIENTE VERIFICACIÓN MANUAL] en el AUDITORIA.md.

### GENERA EL REPORTE:

Crea Documentacion/AUDITORIA_DOCUMENTACION.md con:

**Para cada documento:**
```
## [Nombre del documento]
Estado: ACTUALIZADO ✓ | CON CORRECCIONES ⚠ | REQUIERE REVISIÓN MANUAL ✗

Correcciones aplicadas:
- Campo [X]: era "[valor incorrecto]" → corregido a "[valor del código]"
- Campo [Y]: era "[valor incorrecto]" → corregido a "[valor del código]"

Pendiente verificación manual:
- [dato que no pudo verificarse contra el código]
```

**Resumen final:**
- Total documentos revisados: N
- Total correcciones aplicadas: N  
- Total pendientes manuales: N
- Porcentaje de coherencia documentación/código: N%

Al terminar di exactamente cuántas correcciones hiciste en cada documento.
```

---

## PASO 3 — TERCER PROMPT: MockUps de interfaz

**Propósito:** Generar mockups HTML que muestren la interfaz REAL del proyecto,
usando los datos reales extraídos de VERDAD_PROYECTO.md.

---

```
Usa Documentacion/VERDAD_PROYECTO.md para obtener los datos reales del proyecto.
Genera 6 MockUps HTML de la interfaz real de Trato Hecho.
Guárdalos en Documentacion/mockups/

## REGLA FUNDAMENTAL
Cada mockup debe mostrar datos reales del proyecto:
- La URL del webhook real (de VERDAD_PROYECTO.md)
- Los componentes React reales (de VERDAD_PROYECTO.md)
- El formato de número de cotización real (de VERDAD_PROYECTO.md)
- Los precios reales: Básico $8.500/m², Premium $15.000/m², Deportivo $12.000/m²
- La fórmula real: m2_final = CEIL(largo × ancho × 1.10)
- Instalación: +$4.500/m²

## DISEÑO (colores del proyecto)
- Azul primario: #1F497D
- Azul medio: #2E75B6
- Verde: #1D9E75
- Blanco: #FFFFFF
- Gris claro: #F5F5F5
- Tipografía: Arial
- Responsive: mobile-first (375px) + desktop (1280px)

## MOCKUP 1 — Página principal con widget cerrado
Archivo: Documentacion/mockups/01_pagina_principal.html

Mostrar sitio completo de Césped Sintético SpA:
- Header: logo "Trato Hecho" + "Césped Sintético SpA · Melipilla, Chile"
- Hero section: "Pasto sintético de calidad para tu hogar y cancha"
- Botones de navegación: Jardines · Deportivo · Calculadora · Contacto
- FAB (floating action button) en esquina inferior derecha:
  · Círculo azul #1F497D · 60px diámetro
  · Ícono de chat blanco
  · Badge rojo "1" (nueva notificación)
  · Al hacer hover: tooltip "¡Cotiza gratis! Respuesta inmediata 24/7"
- Footer con datos del negocio

Comentario HTML al final:
<!-- 
  COMPONENTE REACT: ChatWidget.jsx
  ESTADO: useState(isOpen) en ChatWidget
  ENDPOINT: POST [URL del código desde VERDAD_PROYECTO.md]
-->

## MOCKUP 2 — Chat widget abierto (conversación real de cotización)
Archivo: Documentacion/mockups/02_chat_conversacion.html

Ventana flotante 380×560px con la conversación real del flujo COTIZAR:
- Header azul: avatar "Q" + "Queno · Asesor Trato Hecho" + punto verde "En línea" + botón X
- Conversación completa (simular flujo real):
  · Bot: "¡Hola! Soy Queno 🌿 ¿Para qué espacio necesitas el pasto sintético? ¿Jardín residencial o cancha deportiva?"
  · Usuario: "Para mi jardín"
  · Bot: "Perfecto ✅ Para jardines tenemos dos opciones: Pasto Básico (20mm) a $8.500/m² o Pasto Premium (35mm) a $15.000/m². ¿Cuántos metros cuadrados tiene tu espacio?"
  · Usuario: "5 por 8 metros"
  · Bot: "Calculé tu espacio: 5×8 = 40 m². Con el margen de instalación del 10% necesitas 44 m². ¿Incluyes el servicio de instalación profesional? (+$4.500/m²)"
  · Usuario: "Sí, con instalación"
  · Bot: "💰 Resumen de tu cotización:
         • Producto: Pasto Básico (20mm)
         • Superficie: 44 m² (margen 10% incluido)
         • Material: 44 × $8.500 = $374.000
         • Instalación: 44 × $4.500 = $198.000
         • TOTAL: $572.000 CLP
         Para generar tu cotización formal necesito tu nombre completo."
  · Usuario: "Juan Pérez González"
  · Bot: "Gracias Juan. ¿Cuál es tu RUT?"
- Input de texto con placeholder "Escribe tu mensaje..." + botón enviar azul
- Indicador de escritura (tres puntos animados) mientras "el bot escribe"

Comentario HTML al final:
<!-- 
  COMPONENTES REACT: ChatWindow.jsx + ChatMessage.jsx + useChat.js
  HOOK: useChat() → { messages, sendMessage, isLoading, uuid }
  UUID almacenado en: [localStorage/sessionStorage - según VERDAD_PROYECTO.md]
-->

## MOCKUP 3 — QuoteCard (tarjeta de cotización generada)
Archivo: Documentacion/mockups/03_quote_card.html

La QuoteCard se muestra dentro del chat después de completar los datos:
- Mensaje del bot: "¡Tu cotización está lista! 🎉"
- Tarjeta con borde azul y fondo blanco:
  · Header: "📋 Cotización [número real según VERDAD_PROYECTO.md]"
  · Badge verde "✓ Generada" en la esquina superior derecha
  · Tabla de detalle con exactamente los campos de la tabla PostgreSQL real:
    - Producto: Pasto Básico (20mm)
    - Cliente: Juan Pérez González
    - Superficie: 44 m²
    - Precio/m²: $8.500 CLP
    - Instalación: Incluida (+$4.500/m²)
    - Subtotal material: $374.000 CLP
    - Subtotal instalación: $198.000 CLP
    - TOTAL: $572.000 CLP (negrita, azul, grande)
  · Vigencia: "Válida por 10 días · [fecha actual + 10 días]"
  · Estado: "pendiente" (badge naranja)
- Botón verde "💳 Pagar ahora con MercadoPago →"
- Texto pequeño: "Pago 100% seguro · Tus datos de tarjeta son privados"
- Mensaje de bot: "¡También se le notificó al equipo de Césped Sintético SpA! Recibirás confirmación en breve."

Comentario HTML al final:
<!-- 
  COMPONENTE REACT: QuoteCard.jsx
  DATOS: response.quote (objeto de la BD)
  TABLA BD: [nombre real desde VERDAD_PROYECTO.md]
-->

## MOCKUP 4 — Calculadora de m²
Archivo: Documentacion/mockups/04_calculadora.html

P�gina completa con header del sitio + calculadora prominente:
- Título: "Calculadora de Metros Cuadrados"
- Descripción: "Calcula exactamente cuánto pasto sintético necesitas. Incluimos un 10% adicional para cortes y ajustes de instalación."
- Formulario:
  · Label + Input "Largo del espacio (metros)" · placeholder "Ej: 5.5"
  · Label + Input "Ancho del espacio (metros)" · placeholder "Ej: 8"
  · Botón azul grande "Calcular metros cuadrados"
- Sección resultado (hidden hasta calcular):
  · "📐 Área base: [largo × ancho] m²"
  · "🔧 Margen de instalación (10%): +[área×0.10] m²"
  · "✅ Total recomendado: [CEIL(área×1.10)] m²"
  · Separador + "Estimado de precios:"
  · Tabla: Básico 20mm | [m²] × $8.500 | $[total]
           Premium 35mm | [m²] × $15.000 | $[total]
           Deportivo 25mm | [m²] × $12.000 | $[total]
  · Botón verde "Cotizar esta cantidad en el chat →"
- Validación de errores en rojo bajo cada input (para 0, negativos y texto)
- Botón de cálculo deshabilitado mientras hay errores

Comentario HTML al final:
<!-- 
  COMPONENTE REACT: Calculator.jsx
  FÓRMULA: Math.ceil(largo * ancho * 1.10)
  NO usa API · cálculo 100% en frontend
-->

## MOCKUP 5 — Panel de gestión (login)
Archivo: Documentacion/mockups/05_panel_login.html

Pantalla de login del panel administrativo (JWT):
- Fondo gris suave #F5F5F5
- Tarjeta centrada max-width 400px con sombra sutil:
  · Logo: círculo azul #1F497D con letra "T" blanca + "Trato Hecho"
  · Subtítulo: "Panel de Gestión · Solo para el equipo de Césped Sintético SpA"
  · Input "Usuario" con ícono de persona gris
  · Input "Contraseña" con ícono candado + botón ojo para mostrar/ocultar
  · Checkbox "Mantener sesión iniciada"
  · Botón azul #1F497D ancho completo "Iniciar sesión"
  · Link centrado "¿Olvidaste tu contraseña? → Recuperar acceso"
- Mensaje de error (ejemplo): "❌ Credenciales incorrectas. Intento 1 de 3."
- Footer: "🔒 Acceso protegido · Sesión JWT · Sistema Trato Hecho"

Comentario HTML al final:
<!--
  ENDPOINT: POST /api/auth/login · { username, password }
  RESPUESTA: { token: JWT, user: { nombre, rol } }
  ALMACENAMIENTO: localStorage.setItem('trato_hecho_token', token)
  EXPIRACIÓN: 8 horas
-->

## MOCKUP 6 — Panel de gestión (dashboard de cotizaciones)
Archivo: Documentacion/mockups/06_panel_dashboard.html

Dashboard completo con datos reales del proyecto:
- Sidebar izquierdo 240px:
  · Logo + "Trato Hecho" en header
  · Menú: 📊 Dashboard (activo) | 📋 Cotizaciones | ⚙️ Configuración | 🚪 Cerrar sesión
  · Footer sidebar: versión del sistema + nombre del usuario

- Header principal:
  · "Panel de Gestión" a la izquierda
  · "Propietario · Césped Sintético SpA" + avatar con iniciales a la derecha

- KPIs (4 tarjetas en fila):
  · 🔴 "3 Pendientes" · fondo #FFF0F0 · borde #B85450
  · 🟢 "12 Aprobadas" · fondo #E6F7E6 · borde #297520
  · ⭕ "0 Rechazadas" · fondo #F5F5F5 · borde #888780
  · 💰 "$8.947.000 CLP" · fondo #E8F0FA · borde #1F497D
  · (total recaudado en cotizaciones aprobadas)

- Filtros (pills clickeables): [Todas ●15] [Pendiente ●3] [Aprobada ●12] [Rechazada ●0]

- Tabla de cotizaciones (usar campos reales de la tabla PostgreSQL):
  Número | Nombre | Producto | m² | Total | Estado | Fecha | Acciones

  COT-2026-003 | Juan Pérez G. | Básico 20mm | 44 m² | $572.000 | 🔴 Pendiente | Hoy 14:32 | [Ver]
  COT-2026-002 | María García R. | Deportivo 25mm | 120 m² | $1.980.000 | 🟢 Aprobada | Ayer 09:15 | [Ver]
  COT-2026-001 | Carlos López M. | Premium 35mm | 22 m² | $429.000 | 🟢 Aprobada | 18/05 11:00 | [Ver]

- Modal "Ver detalle" (visible para COT-2026-003):
  Todos los campos de la tabla PostgreSQL real incluyendo:
  · session_id (UUID)
  · rut del cliente
  · dirección de instalación
  · estado actual con dropdown para cambiarlo

- Paginación: ← 1 2 3 → · Mostrando 3 de 15 cotizaciones

Comentario HTML al final:
<!--
  ENDPOINTS:
  GET /api/cotizaciones?estado=pendiente → lista filtrada
  GET /api/cotizaciones/:id → detalle
  PUT /api/cotizaciones/:id/estado → actualizar estado
  TABLA BD: [nombre real desde VERDAD_PROYECTO.md]
  AUTENTICACIÓN: Authorization: Bearer {JWT} en cada request
-->

## DESPUÉS DE CREAR LOS 6 MOCKUPS

Genera Documentacion/mockups/README.md con:
- Tabla de los 6 mockups: nombre | pantalla que representa | componente React | endpoint
- Instrucciones para abrirlos: "Abrir directamente en el navegador (doble clic)"
- Nota: "Mockups estáticos HTML. Datos representativos del sistema real."
```

---

## PASO 4 — CUARTO PROMPT: Diagramas UML adicionales

---

```
Genera 2 diagramas draw.io adicionales requeridos por la guía 2.1.2 de DuocUC.
Usa SIEMPRE Documentacion/VERDAD_PROYECTO.md para los datos reales.
Guárdalos en Documentacion/diagramas/

## DIAGRAMA 1 — Casos de Uso
Archivo: Documentacion/diagramas/Trato_Hecho_Casos_Uso.drawio

Formato UML estándar (notación UML clásica):

Actores:
- Cliente → persona icon izquierda
- Propietario del Negocio → persona icon derecha
- <<sistema>> Claude API → rectángulo punteado arriba
- <<sistema>> MercadoPago → rectángulo punteado arriba
- <<sistema>> Telegram → rectángulo punteado derecha superior

Sistema Trato Hecho (rectángulo grande que engloba los casos de uso):

CASOS DE USO DEL CLIENTE (óvalo UML):
UC-01: Iniciar conversación con agente IA
UC-02: Calcular m² (calculadora)
UC-03: Indicar tipo de espacio (jardín/deportivo)
UC-04: Ingresar medidas del espacio
UC-05: Confirmar instalación profesional
UC-06: Entregar datos personales (nombre, RUT, dirección)
UC-07: Recibir cotización [formato real de VERDAD_PROYECTO.md]
UC-08: Pagar con MercadoPago
UC-09: Retomar cotización vigente (10 días)

CASOS DE USO DEL PROPIETARIO (óvalo UML):
UC-10: Autenticarse en panel (JWT)
UC-11: Ver listado de cotizaciones
UC-12: Filtrar cotizaciones por estado
UC-13: Ver detalle completo de cotización
UC-14: Recibir notificación de nueva cotización
UC-15: Recibir confirmación de pago

RELACIONES UML:
- Cliente → UC-01, UC-02, UC-03, UC-04, UC-05, UC-06, UC-07, UC-08, UC-09
- Propietario → UC-10, UC-11, UC-12, UC-13, UC-14, UC-15
- UC-01 <<include>> UC-03 (el tipo de espacio es parte obligatoria del chat)
- UC-01 <<include>> UC-04 (las medidas son parte obligatoria del chat)
- UC-07 <<extend>> UC-08 (el pago extiende opcionalmente a la cotización)
- UC-09 <<extend>> UC-08 (retomar cotización también puede llevar al pago)
- UC-14 <<include>> UC-07 (toda cotización dispara notificación)
- UC-15 <<include>> UC-08 (todo pago dispara notificación)
- Línea punteada de dependencia: Claude API → UC-01 (el chat usa Claude)
- Línea punteada de dependencia: MercadoPago → UC-08 (el pago usa MP)
- Línea punteada de dependencia: Telegram → UC-14, UC-15

Colores del proyecto:
- Actores: #1F497D fondo blanco texto
- UC Cliente: #EBF3FF borde #1F497D
- UC Propietario: #D5E8D4 borde #297520
- Sistemas externos: #FFF2CC borde #D6B656 estilo dashed

## DIAGRAMA 2 — Gestión de Usuarios y Autenticación JWT
Archivo: Documentacion/diagramas/Trato_Hecho_Gestion_Usuarios.drawio

Diagrama de flujo con 4 swim lanes:
- Carril 1 (gris): Propietario
- Carril 2 (morado #E8DEF8): Frontend React
- Carril 3 (amarillo #FFF2CC): Backend / n8n
- Carril 4 (verde #D5E8D4): PostgreSQL

FLUJO A — Login exitoso:
[Propietario] Ingresa usuario y contraseña
→ [Frontend] Valida que campos no estén vacíos
→ [Frontend] POST [endpoint de login desde VERDAD_PROYECTO.md o /api/auth/login]
→ [Backend] Verifica credenciales en tabla usuarios
→ [PostgreSQL] Retorna usuario si existe
→ [Backend] Genera JWT firmado · expiración 8 horas
→ [Frontend] Recibe { token, user }
→ [Frontend] Guarda JWT en localStorage
→ [Frontend] Redirige a /dashboard

FLUJO B — Login fallido:
[Propietario] Ingresa credenciales incorrectas
→ [Backend] Retorna HTTP 401 { error: "Credenciales inválidas" }
→ [Frontend] Muestra mensaje de error rojo
→ [Frontend] Al 3er intento: bloquea formulario 5 minutos

FLUJO C — Acceso a ruta protegida:
[Propietario] Navega a /dashboard
→ [Frontend] Lee JWT de localStorage
→ [Frontend] Agrega header Authorization: Bearer {token}
→ [Backend] Middleware verifica firma JWT y expiración
→ Si válido: [Backend] Procesa la petición
→ Si expirado/inválido: [Backend] HTTP 401 → [Frontend] Redirige a /login

FLUJO D — Recuperar contraseña:
[Propietario] Clic en "¿Olvidaste tu contraseña?"
→ [Frontend] Muestra campo de email
→ [Backend] Busca email en tabla usuarios
→ [Backend] Genera token temporal en Redis · TTL 1 hora
→ [Backend] Envía correo con link de recuperación
→ [Propietario] Clic en link → nueva contraseña
→ [Backend] Valida token Redis → actualiza hash en PostgreSQL
→ [Backend] Elimina token de Redis

Tabla usuarios PostgreSQL (mini-ERD incluido en el diagrama):
id SERIAL PK | username VARCHAR UNIQUE | password_hash VARCHAR |
email VARCHAR | rol VARCHAR DEFAULT 'admin' | created_at TIMESTAMP | ultimo_acceso TIMESTAMP

Mismos colores del resto de diagramas del proyecto.
```

---

## PASO 5 — QUINTO PROMPT: README.md profesional

---

```
Genera el README.md principal del repositorio GitHub del proyecto Trato Hecho.
Usa SIEMPRE Documentacion/VERDAD_PROYECTO.md para URLs, puertos, versiones y
cualquier dato técnico. NO uses datos inventados.
Guárdalo en la raíz del repositorio como README.md.

## ESTRUCTURA REQUERIDA

### 1. Badges (primera línea)
Usa los datos reales de VERDAD_PROYECTO.md:
![Estado](https://img.shields.io/badge/Estado-En%20Producción-1D9E75)
![DuocUC](https://img.shields.io/badge/DuocUC-TPY1101-1F497D)
![React](https://img.shields.io/badge/React-[versión real]-61DAFB?logo=react)
![n8n](https://img.shields.io/badge/n8n-Self--Hosted-EA4B71)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-[versión real]-336791?logo=postgresql)
![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E?logo=railway)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?logo=vercel)

### 2. Título y descripción (concisa)
# Trato Hecho 🌿
Descripción en 2 líneas máximo. Qué hace y para quién.

### 3. El problema que resuelve
3 bullets concretos. Usar datos reales del proyecto ($5M, 2-4 días, etc.)

### 4. Arquitectura del sistema
Diagrama ASCII de las 4 capas reales:
```
[Cliente]
    ↓ POST [endpoint real de VERDAD_PROYECTO.md]
[Frontend React - Vercel]
    ↓
[Orquestador n8n - Railway + Docker]
    ↓ 23 nodos · 3 ramas
[Claude API]   [PostgreSQL + Redis]   [Telegram · Gmail · MercadoPago]
```

### 5. Stack tecnológico
Tabla con versiones REALES de VERDAD_PROYECTO.md:
| Capa | Tecnología | Versión | Hosting |

### 6. Estructura del repositorio
Árbol de carpetas REAL del estado actual del repositorio:
```
trato-hecho/
├── Documentacion/
│   ├── word/         # 7 documentos .docx
│   ├── diagramas/    # 9 diagramas .drawio
│   ├── mockups/      # 6 mockups .html
│   └── historias-usuario/  # 1 archivo .xlsx
├── Producto/
│   ├── frontend/     # React 18 + Vite
│   └── n8n/          # workflow JSON + scripts
└── Gestion/
    ├── planificacion/ # Carta Gantt
    └── riesgos/       # Matriz de riesgos
```

### 7. Cómo levantar el proyecto localmente
Comandos REALES extraídos de docker-compose.yml y package.json:
```bash
# 1. Clonar
git clone [URL real del repo]
cd trato-hecho

# 2. Variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Backend
docker-compose up -d

# 4. Frontend
cd Producto/frontend
npm install
npm run dev
```

### 8. Variables de entorno
Template .env con TODAS las variables reales (sin valores):
```
N8N_PORT=[puerto real]
POSTGRES_USER=
POSTGRES_PASSWORD=
ANTHROPIC_API_KEY=
MERCADOPAGO_ACCESS_TOKEN=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

### 9. Equipo
| Nombre | Rol | Responsabilidad |
| Andrés Romero | Líder técnico | Arquitectura n8n · Integración · Railway |
| Manuel Carvajal | Frontend/UX | React.js · Calculadora · Panel admin |
| Cristofer San Martín | Backend/QA | Telegram · SMTP · MercadoPago · Pruebas |

### 10. Documentación disponible
Tabla con los 7 documentos y links relativos:
| # | Documento | Descripción |

### 11. Estado EP2 (evaluación 30 mayo 2026)
Tabla: Requisito mínimo | Estado | Evidencia
Los 11 requisitos del profesor con ✓/⚠/✗

### 12. Licencia
MIT License · Proyecto académico DuocUC 2026

IMPORTANTE: El README debe ser en español. Máximo 300 líneas.
NO inventes URLs ni datos de producción que no estén en VERDAD_PROYECTO.md.
Si una URL no está en el código, escribe [URL pendiente de configurar].
```

---

## PASO 6 — SEXTO PROMPT: Presentación PowerPoint EP2

---

```
Genera la presentación para la Evaluación Parcial 2 de DuocUC del proyecto Trato Hecho.
Archivo: Documentacion/EP2_Presentacion_TratoHecho.pptx

## REGLA FUNDAMENTAL
Usa Documentacion/VERDAD_PROYECTO.md para TODOS los datos técnicos.
Si necesitas un dato técnico que no está en VERDAD_PROYECTO.md,
escribe [COMPLETAR CON DATO REAL] en el slide para que el equipo lo complete.

## ESPECIFICACIONES
- 16:9 · Arial · Duración objetivo: 20 minutos exactos
- Paleta: Fondo #FFFFFF · Títulos #1F497D · Acentos #2E75B6 · Texto #333333
- Footer en todos los slides: "Trato Hecho · EP2 · DuocUC 2026"
- Número de slide en esquina inferior derecha (excepto portada)

## SLIDES (16 total)

**SLIDE 1 — PORTADA** (1 min)
Fondo azul #1F497D · Texto blanco
- "TRATO HECHO" grande · "Sistema de Cotización con Agente IA"
- "Evaluación Parcial 2 · DuocUC · TPY1101 · 35% nota final"
- "Cliente: Césped Sintético SpA · Melipilla, Chile"
- "Andrés Romero · Manuel Carvajal · Cristofer San Martín · Mayo 2026"

**SLIDE 2 — AGENDA** (30 seg)
Numerar los 11 puntos obligatorios del profesor con tiempo estimado cada uno.
"Demostración en vivo disponible al final"

**SLIDE 3 — EL PROBLEMA** (1.5 min)
Datos REALES del problema:
- "$5.000.000 CLP anuales en ventas perdidas"
- "2 a 4 días hábiles de tiempo de respuesta promedio"
- "Pedidos con metraje incorrecto por medición manual"
- "0 herramientas digitales antes de Trato Hecho"
Foto/imagen representativa de un jardín con pasto sintético (si disponible)

**SLIDE 4 — METODOLOGÍA** (1 min)
Scrum adaptado con evidencias reales:
- Sprints semanales (15 semanas · marzo → mayo 2026)
- 3 roles: Líder técnico · Frontend/UX · Backend/QA
- Herramientas: GitHub (control de versiones) · Carta Gantt (planificación)
- Revisión de avance: viernes de cada semana
Diagrama simple del ciclo: Planificar → Desarrollar → Revisar → Entregar

**SLIDE 5 — REGLAS DE NEGOCIO E HISTORIAS DE USUARIO** (1.5 min)
Tabla resumen de las 7 épicas (datos reales):
| Épica | HU | Criterios |
E1 Chat con Agente IA | 5 | 15
E2 Calculadora m² | 2 | 6
E3 Generación Cotizaciones | 3 | 9
E4 Notificaciones | 2 | 6
E5 Pago en Línea | 2 | 6
E6 Panel de Gestión | 2 | 6
E7 Seguridad y Disponibilidad | 2 | 6
TOTAL | 18 historias | 54 criterios

Ejemplo de HU con criterio de aceptación:
"Como cliente, quiero proporcionar medidas como '5x8' para que el sistema calcule
los m² automáticamente. CA: formato '5x8' → CEIL(5×8×1.10) = 44 m²"

**SLIDE 6 — ARQUITECTURA DE LA SOLUCIÓN** (2 min)
Diagrama de 4 capas (datos de VERDAD_PROYECTO.md):
CAPA 1: Cliente (navegador)
CAPA 2: Frontend React [versión real] → Vercel
CAPA 3: Orquestador n8n → Railway Docker [23 nodos · 3 ramas]
CAPA 4a: Servicios → Claude Sonnet [modelo real] · MercadoPago · Telegram · Gmail
CAPA 4b: Persistencia → PostgreSQL [versión real] · Redis 7

Datos clave del flujo:
"POST [endpoint real] → n8n procesa → Claude responde → [COTIZAR|PAGAR|CHAT]"

**SLIDE 7 — TECNOLOGÍAS Y LENGUAJES** (1.5 min)
Grid visual con tecnología + función + justificación:
React [versión real] → "Interfaz dinámica sin recargar página"
n8n → "Orquestador visual de flujos (open source · $0)"
Claude Sonnet [modelo real] → "IA conversacional que entiende lenguaje natural"
PostgreSQL [versión real] → "Fuente de verdad de cotizaciones"
Redis 7 → "Caché velocidad + TTL automático"
MercadoPago → "Checkout integrado en el chat · CLP nativo"
Telegram Bot → "Notificación instantánea al smartphone"
JWT → "Autenticación sin estado para el panel"

"Presupuesto en licencias: $0 CLP · 100% open source o planes gratuitos"

**SLIDE 8 — MODELO DE BASE DE DATOS** (1.5 min)
Visual tipo ERD simplificado con los campos REALES de VERDAD_PROYECTO.md:
Tabla [nombre real]:
🔑 id | SERIAL PK
📄 [campo número] | [tipo real] · UNIQUE · Formato: [formato real]
Y todos los campos reales encontrados en el código...

Fórmula de cálculo real:
m2_margen = CEIL(largo × ancho × 1.10)
total = m2_margen × precio + (instalacion ? m2_margen × 4500 : 0)

**SLIDE 9 — BOSQUEJO DE INTERFAZ** (1.5 min)
4 imágenes en grid 2×2 (agregar screenshots reales o los mockups HTML):
1. Página principal con widget FAB
2. Chat abierto con conversación de cotización
3. QuoteCard con cotización generada
4. Panel de gestión con listado

"[REEMPLAZAR CON SCREENSHOT REAL DEL SISTEMA EN PRODUCCIÓN]"
(placeholder para que el equipo agregue la imagen real)

**SLIDE 10 — GESTIÓN DE USUARIOS Y MANTENEDORES** (1.5 min)
Flujo de autenticación JWT simplificado:
[Login] → [POST /api/auth/login] → [Validar en BD] → [Generar JWT 8h] → [Dashboard]
                                         ↓ Fallo
                                  [Error · 3 intentos → Bloqueo 5 min]

Funcionalidades del panel:
✓ Login con JWT (8h expiración)
✓ Ver cotizaciones con filtros por estado
✓ Detalle completo incluyendo UUID de sesión
✓ Contador de pendientes sin respuesta
✓ Recuperar contraseña por email
✓ Gestión de usuario administrador

**SLIDE 11 — AMBIENTE DE PRUEBAS** (1.5 min)
Tabla de ambientes (datos de VERDAD_PROYECTO.md):
| Componente | Desarrollo | Producción |
| Frontend | localhost:[puerto real] | Vercel |
| n8n | localhost:[puerto real] | Railway |
| PostgreSQL | Docker local | Railway managed |
| Redis | Docker local | Railway Redis |
| MercadoPago | Sandbox TEST-xxxx | [Pendiente producción] |
| Claude | [modelo real] | [mismo modelo] |

Herramientas de prueba: Postman · Chrome DevTools · Lighthouse · UptimeRobot

**SLIDE 12 — ASPECTOS DE INTEGRACIÓN** (1.5 min)
Los 8 actores del diagrama de secuencia:
Cliente → Frontend → n8n → Redis → Claude API → PostgreSQL → Telegram/Gmail → MercadoPago

Métricas REALES obtenidas (si están en la documentación, sino [PENDIENTE MEDICIÓN]):
· Respuesta chat: [dato real o PENDIENTE]
· Generación cotización: [dato real o PENDIENTE]
· Notificación Telegram: [dato real o PENDIENTE]
· Carga frontend Lighthouse: [dato real o PENDIENTE]

**SLIDE 13 — PLAN DE PRUEBAS** (1 min)
47 casos de prueba · 7 módulos · IEEE 829

| Módulo | Casos | Estado |
| Chat IA | 10 | [Ejecutado/Pendiente] |
| Calculadora | 6 | [Ejecutado/Pendiente] |
| Cotizaciones | 7 | [Ejecutado/Pendiente] |
| Pagos | 7 | [Ejecutado/Pendiente] |
| Notificaciones | 6 | [Ejecutado/Pendiente] |
| Panel Admin | 6 | [Ejecutado/Pendiente] |
| End-to-End | 5 | [Ejecutado/Pendiente] |

Criterio de éxito: 100% RF Alta aprobados · 0 defectos críticos abiertos

**SLIDE 14 — COHERENCIA Y RESULTADOS** (1 min)
Tabla antes vs después:
| Aspecto | Antes de Trato Hecho | Con Trato Hecho |
| Notificación | 2-4 días hábiles | < [tiempo real medido o 30 seg] |
| Medición m² | Manual (con errores) | Calculadora automática +10% |
| Proceso pago | Transferencia manual | Botón MercadoPago en chat |
| Disponibilidad | Solo horario comercial | 24/7 |
| Costo herramientas | $0 (sin sistema) | $0 (open source) |

**SLIDE 15 — EVIDENCIAS DE AVANCE** (1 min)
Sección para capturas reales:
"[SCREENSHOT 1: Sistema en producción - URL Vercel]"
"[SCREENSHOT 2: Workflow n8n activo en Railway]"
"[SCREENSHOT 3: Notificación Telegram real recibida]"
"[SCREENSHOT 4: Panel de gestión con cotizaciones reales]"
"[SCREENSHOT 5: Proceso de pago sandbox MercadoPago]"

INSTRUCCIÓN AL EQUIPO: Reemplazar estos placeholders con
screenshots reales antes de la presentación del 30 de mayo.

**SLIDE 16 — REPOSITORIO Y CIERRE** (30 seg)
Estructura GitHub visual:
Documentacion/ | Producto/ | Gestion/
[URL del repositorio si disponible]

"¿Preguntas?" · Fondo azul #1F497D · texto blanco
"Trato Hecho · EP2 · DuocUC 2026"
"Andrés Romero · Manuel Carvajal · Cristofer San Martín"

## NOTAS TÉCNICAS PARA PYTHON-PPTX
- Usar python-pptx (NO python-docx)
- Cada slide con footer: "Trato Hecho · EP2 · DuocUC 2026"
- Número de slide en esquina inferior derecha (excepto slide 1 y 16)
- Sin transiciones ni animaciones
- Tamaños: título 32pt bold, subtítulo 20pt, cuerpo 18pt, tabla 14pt
- Espaciado generoso: 20px entre elementos mínimo
```

---

## PASO 7 — SÉPTIMO PROMPT: Commit en rama y Pull Request

---

```
Prepara el commit en la rama docs/ep2-evaluacion-parcial-2 para que
mis compañeros lo revisen antes de hacer merge a main.

## TAREA 1: Verificación pre-commit

Verifica que existen estos archivos (muestra ✓ o ✗ para cada uno):

Documentacion/VERDAD_PROYECTO.md ← fuente de verdad del proyecto
Documentacion/AUDITORIA_DOCUMENTACION.md ← informe de coherencia
Documentacion/word/ ← 7 archivos .docx
Documentacion/diagramas/ ← al menos 9 archivos .drawio
Documentacion/mockups/ ← 6 archivos .html + README.md
Documentacion/historias-usuario/ ← 1 archivo .xlsx
Documentacion/EP2_Presentacion_TratoHecho.pptx
Gestion/planificacion/ ← Carta Gantt
Gestion/riesgos/ ← Matriz de riesgos
README.md ← en la raíz del repositorio

Si falta alguno, avísame ANTES de continuar.

## TAREA 2: Crear .gitignore si no existe

Genera .gitignore con:
node_modules/
.env
.env.local
.env.production
*.log
.DS_Store
Thumbs.db
dist/
build/
.cache/
*.tmp

## TAREA 3: Mostrar git status

Ejecuta: git status
Muéstrame todos los archivos que serán incluidos en el commit.

## TAREA 4: Generar mensaje de commit

Formato Conventional Commits:
```
feat(docs/ep2): documentación completa evaluación parcial 2

Auditoría y corrección de documentación contra código real:
- VERDAD_PROYECTO.md: fuente de verdad extraída del código
- AUDITORIA_DOCUMENTACION.md: [N] correcciones aplicadas en [N] docs

Nuevos documentos EP2:
- MockUps HTML: 6 pantallas (chat, calculadora, cotización, panel admin)
- Diagramas UML: casos de uso + gestión de usuarios JWT
- Presentación PPT: 16 slides para defensa 30 mayo 2026

Estructura de repositorio DuocUC:
- Documentacion/ (word, diagramas, mockups, historias-usuario)
- Producto/ (código fuente)
- Gestion/ (planificación, riesgos)

- README.md: badges + stack real + estructura + guía de instalación

Refs: EP2 DuocUC TPY1101 · Evaluación 30 mayo 2026 · 35% nota final
```

## TAREA 5: Mostrar comandos exactos

Muéstrame EXACTAMENTE qué comandos ejecutar (no los ejecutes tú):
```bash
git add .
git commit -m "feat(docs/ep2): documentación completa evaluación parcial 2

[mensaje completo del paso anterior]"

git push origin docs/ep2-evaluacion-parcial-2
```

## TAREA 6: Instrucciones para el Pull Request en GitHub

Genera el texto completo del PR para que yo lo copie en GitHub:

TÍTULO: "EP2: Documentación completa · Trato Hecho · 30 mayo 2026"

DESCRIPCIÓN (en markdown):
## ¿Qué incluye este PR?
[lista de cambios]

## Checklist de revisión para los colegas
- [ ] VERDAD_PROYECTO.md refleja el código real del proyecto
- [ ] Los mockups muestran la interfaz correcta del sistema
- [ ] Los datos técnicos en la presentación son correctos
- [ ] El README tiene los comandos correctos para levantar el proyecto
- [ ] Los diagramas UML son coherentes con la implementación real
- [ ] No hay URLs o datos de producción incorrectos

## Cómo revisar
1. Clonar la rama: git checkout docs/ep2-evaluacion-parcial-2
2. Abrir los mockups en el navegador (doble clic en .html)
3. Abrir los .drawio en app.diagrams.net
4. Verificar la presentación .pptx en PowerPoint

REVIEWERS: @ManuelCarvajal @CristoferSanMartin
ASSIGNEE: @AndresRomero
LABELS: documentation, ep2, duocuc, review-required
BASE BRANCH: main
COMPARE BRANCH: docs/ep2-evaluacion-parcial-2
```

---

## PASO 8 — LO QUE DEBES HACER TÚ

### 8.1 Agregar screenshots reales a la presentación

Antes del 30 de mayo, reemplaza los placeholders del Slide 15:
1. Entra al sistema en Vercel → screenshot del chat funcionando
2. Entra a Railway → screenshot del workflow n8n activo con ejecuciones
3. Genera una cotización real → screenshot de la notificación Telegram
4. Entra al panel de gestión → screenshot con cotizaciones reales
5. En MercadoPago sandbox → screenshot del proceso de pago

### 8.2 Aprobar el Pull Request

1. Abrir GitHub → tu repositorio → Pull Requests
2. Asignar a Manuel y Cristofer como Reviewers
3. Ellos revisan y aprueban con "Approve"
4. Tú haces: "Merge pull request" → "Squash and merge"
5. "Delete branch" para limpiar

### 8.3 Preparar la defensa (15-20 min preguntas del profesor)

Estudia estas respuestas basándote en VERDAD_PROYECTO.md:

**¿Por qué n8n en lugar de un backend tradicional?**
→ Reduce el código de integración entre servicios externos a un workflow visual versionable. Además es open source ($0 en licencias), se despliega en Docker y tiene conectores nativos para Redis, PostgreSQL, Telegram y SMTP.

**¿Cómo garantizan la unicidad del número de cotización?**
→ Usamos INCR atómico en Redis (th:counter). Redis garantiza atomicidad por diseño: no pueden ocurrir dos incrementos simultáneos que generen el mismo número, incluso bajo carga concurrente.

**¿Qué pasa si Claude no responde en 30 segundos?**
→ n8n tiene timeout configurado de 30 segundos en el nodo HTTP. Si se cumple, el flujo termina con error controlado y el frontend recibe un mensaje de error descriptivo al usuario.

**¿Por qué Redis además de PostgreSQL?**
→ Dos propósitos distintos: PostgreSQL es la fuente de verdad permanente (trazabilidad, reportes, panel admin). Redis es caché de acceso en microsegundos para el historial conversacional (24h TTL) y cotizaciones activas (10 días TTL). Sin Redis, cada mensaje requeriría una consulta SQL, triplicando la latencia del chat.

**¿Cómo aseguran que el monto en MercadoPago es correcto?**
→ El monto NO lo calcula Claude. El cálculo ocurre en el nodo B5 (Construir Prompt) de n8n usando JavaScript determinístico: CEIL(m2 × 1.10) × precio + instalación. MercadoPago recibe ese valor ya calculado como unit_price, sin pasar por la IA.

**¿Cómo protegen los datos de los clientes?**
→ HTTPS en todos los endpoints (Let's Encrypt), credenciales en variables de entorno (nunca en el código), MercadoPago maneja los datos de tarjeta directamente (nosotros no los vemos), JWT con expiración para el panel admin.

---

## RESUMEN EJECUTIVO

| Paso | Quién | Qué hace | Output esperado |
|------|-------|----------|-----------------|
| 0 | TÚ | Crear rama + copiar archivos | Rama lista con estructura DuocUC |
| 1 | Claude Code | Lee código → extrae verdad real | VERDAD_PROYECTO.md |
| 2 | Claude Code | Audita docs vs código → corrige | AUDITORIA.md + docs corregidos |
| 3 | Claude Code | Genera mockups con datos reales | 6 archivos HTML interactivos |
| 4 | Claude Code | Genera diagramas UML reales | 2 archivos .drawio |
| 5 | Claude Code | README con datos del código | README.md profesional |
| 6 | Claude Code | PPT con [PENDIENTE] donde faltan datos | .pptx 16 slides |
| 7 | Claude Code | Commit + instrucciones PR | Rama lista para review |
| 8a | TÚ | Screenshots reales → PPT Slide 15 | PPT 100% completo |
| 8b | TÚ | Manuel y Cristofer aprueban el PR | Merge a main |
| 8c | TÚ | Ensayo 20 min + preparar defensa | Listo para 30/05 |

**Tiempo estimado Claude Code:** 60-75 minutos
**Tiempo estimado de tu parte:** 2-3 horas (screenshots + ensayo)
**Fecha límite:** 29 mayo 2026 (día antes de la evaluación)

---

## NOTA SOBRE [PENDIENTE VERIFICACIÓN MANUAL]

En la presentación y el README aparecerán algunos marcadores [COMPLETAR CON DATO REAL].
Esto es INTENCIONAL y significa que Claude Code no encontró ese dato en el código.
El equipo debe completarlos antes del 30 de mayo con la información real.
Ejemplos comunes:
- URL de producción en Vercel (si no está hardcodeada en el código)
- Número de commits totales en el repositorio
- Screenshots del sistema en producción
- Métricas de tiempo reales medidas (Lighthouse, cronómetro)
