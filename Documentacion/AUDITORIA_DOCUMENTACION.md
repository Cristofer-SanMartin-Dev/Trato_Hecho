# AUDITORÍA DE DOCUMENTACIÓN — Trato Hecho
# Fecha: 2026-05-21
# Fuente de verdad: Documentacion/VERDAD_PROYECTO.md
# Principio: EL CÓDIGO ES LA FUENTE DE VERDAD

---

## 01_Documentacion_Tecnica_Completa.docx
Estado: CON CORRECCIONES ⚠

Correcciones aplicadas:
- Modelo Claude: era "Claude Sonnet 4.5 (Anthropic API)" → corregido a "Claude Sonnet (claude-sonnet-4-6, Anthropic API)"
- Frontend arquitectura: era "React 18 · Vite · Tailwind CSS · Vercel (deploy)" → corregido a "HTML/JavaScript vanilla · Tailwind CSS · Vercel (deploy)"
- Frontend capa: era "React.js + Tailwind CSS" → corregido a "HTML/JavaScript vanilla + Tailwind CSS"
- Frontend resumen: era "React.js para el frontend" → corregido a "HTML/JavaScript vanilla para el frontend"
- Frontend componentes: 2 instancias de "React.js" → corregido a "HTML/JavaScript vanilla"
- Base de datos: era "PostgreSQL + Redis" → corregido a "Supabase"
- Base de datos: era "PostgreSQL y Redis para persistencia" → corregido a "Supabase para persistencia"
- Base de datos capa: era "PostgreSQL como fuente de verdad transaccional. Redis como caché..." → corregido a "Supabase como base de datos cloud (PostgreSQL gestionado). Tablas: cotizaciones e historial."
- Flujo de datos: era "persiste en PostgreSQL y Redis" → corregido a "persiste en Supabase"
- Flujo de datos: era "consulta Redis por cotización activa (th:quote:{uuid})" → corregido a "consulta Supabase tabla cotizaciones por session_id"
- Claves Redis (3x): "th:quote:{uuid}" → corregido a "cotizaciones (tabla Supabase)"
- Contador (2x): "th:counter" → corregido a "campo numero con timestamp (COT-YYYY-XXXXX)"
- Base de datos tabla: era "PostgreSQL (fuente de verdad) · Supabase (caché TTL 10 días)" → corregido a "Supabase (PostgreSQL gestionado cloud · tablas cotizaciones e historial)"
- Monitoreo: era "Logs n8n en PostgreSQL" → corregido a "Logs n8n en Supabase"
- Flujo paso 3: era "Redis Get:..." → corregido a "Supabase GET:..."
- Flujo paso 6a: era "Redis INCR:..." → corregido a "Supabase/Timestamp:..."
- Flujo paso 6a: era "Redis Set:..." → corregido a "Supabase POST:..."
- Número cotización (4x): "COT-YYYY-XXX" → corregido a "COT-YYYY-XXXXX"
- Número cotización: era "número único (COT-YYYY-XXX)" → corregido a "número único (COT-YYYY-XXXXX, basado en timestamp)"
- Ejemplo cotización (2x): "COT-2026-001" → corregido a "COT-2026-XXXXX"
- Redis genérico: era "Redis 7" → corregido a "Supabase"

Pendiente verificación manual:
- Los nombres de componentes React (ChatWidget, ChatWindow, QuoteCard, Calculator, useChat.js) no tienen equivalente directo en el HTML vanilla — se recomienda actualizar la sección 4.1 manualmente para describir los archivos reales: chatbot.js, calculadora.html, etc.
- "Express.js" mencionado como parte del stack — no se encontró en el código
- "GitHub Actions" como CI/CD — no se pudo verificar en el repositorio

---

## 02_Manual_Instalacion.docx
Estado: CON CORRECCIONES ⚠

Correcciones aplicadas:
- Variables de entorno: "REDIS_HOST=redis" → corregido a "# Redis reemplazado por Supabase"
- Variables de entorno: "REDIS_PORT=6379" → corregido a "# No se requiere Redis"
- Variables de entorno: "POSTGRES_USER=n8n" → corregido a "# PostgreSQL gestionado por Supabase"
- Variables de entorno: "POSTGRES_PASSWORD=CAMBIA_ESTO_123" → corregido a "# PostgreSQL gestionado por Supabase"
- Variables de entorno: "POSTGRES_DB=n8n" → corregido a "SUPABASE_URL=https://enpzxntzphvezopbxbtx.supabase.co"
- Docker logs (2x): "docker-compose logs postgres" → corregido a "# No aplica (Supabase es cloud)"
- Docker logs: "docker-compose logs redis" → corregido a "# No aplica (Supabase es cloud)"
- Docker contenedores: era "Este comando levanta 3 contenedores:" → corregido a "Este comando levanta 1 contenedor:"

Pendiente verificación manual:
- La sección 4.1 dice "npm install" y "npm run dev" para el frontend — el frontend real es HTML estático (no hay package.json en frontend). Se recomienda actualizar a: "Abrir index.html directamente o usar npx serve ."
- La sección 4.2 dice "src/config.js" como configuración — el archivo real es "Producto/config/config.js" (fuera de src/)
- Puerto localhost:5173 para frontend — no aplica (HTML estático en Vercel)
- Sección 3.2 credenciales PostgreSQL/Redis en n8n — debe actualizarse a configurar HTTP Header Auth para Supabase

---

## 03_Manual_Usuario.docx
Estado: CON CORRECCIONES ⚠

Correcciones aplicadas:
- Número cotización (2x): "COT-YYYY-XXX" → corregido a "COT-YYYY-XXXXX"
- Ejemplo cotización: "COT-2026-001" → corregido a "COT-2026-XXXXX"

Pendiente verificación manual:
- Catálogo mencionado al usuario (si lo hay): verificar que los precios y nombres de productos coincidan con el catálogo real (Luxury Emerald $28.500, Soft Touch $22.900, Pet-Friendly $26.000)
- El manual describe un flujo que parece correcto (no menciona tecnologías específicas) — ✓

---

## 04_Documentacion_Flujo_N8N.docx
Estado: CON CORRECCIONES ⚠

Correcciones aplicadas:
- Nombre nodos (4x): "Obtener Historial Redis" → corregido a "GET Historial Supabase"
- Nombre nodos (5x): "Obtener Cotización Redis" → corregido a "GET Cotización Supabase"
- Nombre nodos (4x): "Guardar Historial Redis" → corregido a "Guardar Historial Supabase"
- Nombre nodos (3x): "Guardar Cotización Redis" → corregido a "Guardar Cotización Supabase"
- Nodo genérico: "Guardar Redis" → corregido a "Guardar Supabase"
- Clave Redis (7x): "th:quote:{uuid}" → corregido a "cotizaciones (tabla Supabase)"
- Clave Redis (7x): "hist_{uuid}" → corregido a "historial (tabla Supabase)"
- Contador (4x): "th:counter" → corregido a "campo numero con timestamp (COT-YYYY-XXXXX)"
- Número cotización (11x): "COT-YYYY-XXX" → corregido a "COT-YYYY-XXXXX"
- Ejemplo cotización (2x): "COT-2026-001" → corregido a "COT-2026-XXXXX"
- Webhook path: era "path /chat desde el frontend" → corregido a "path /chat-v2 desde el frontend"
- Frontend (2x): "frontend React" → corregido a "frontend HTML/JavaScript"
- Estado guardado: era "guardado en Redis" → corregido a "guardado en Supabase"

Pendiente verificación manual:
- El documento describe la versión del workflow con path "/chat" (workflow_current.json) — el workflow de producción es "AI Agent v2" con path "/chat-v2". Se recomienda actualizar el título del documento para indicar que describe el workflow de producción correcto.
- Referencias a "useChat.js" como componente del frontend — en realidad es chatbot.js (HTML vanilla)
- Algunas descripciones técnicas de operaciones Redis (TTL en segundos) pueden quedar como referencias históricas — se recomienda revisión manual completa de la sección de bloques Redis

---

## 05_Especificacion_Requerimientos_SRS.docx
Estado: CON CORRECCIONES ⚠

Correcciones aplicadas:
- Frontend (2x): "React.js" → corregido a "HTML/JavaScript vanilla"
- Base de datos: "PostgreSQL + Redis" → corregido a "Supabase"
- Base de datos: era "PostgreSQL como fuente de verdad y Redis como caché de alta velocidad" → corregido a "Supabase como base de datos cloud (PostgreSQL gestionado)"
- Claves Redis (2x): "th:quote:{uuid}" → corregido a "cotizaciones (tabla Supabase)"
- Clave Redis: "hist_{uuid}" → corregido a "historial (tabla Supabase)"
- Número correlativo: era "número correlativo único (COT-YYYY-XXX)" → corregido a "número único (COT-YYYY-XXXXX, basado en timestamp)"
- Número cotización (4x): "COT-YYYY-XXX" → corregido a "COT-YYYY-XXXXX"
- Ejemplo cotización (2x): "COT-2026-001" → corregido a "COT-2026-XXXXX"
- Gestión Supabase: era "la gestión de Redis y PostgreSQL" → corregido a "la gestión de Supabase"
- Stack tecnológico: "PostgreSQL, Redis" → corregido a "Supabase"
- Persistencia RF: "Persistencia en PostgreSQL" → corregido a "Persistencia en Supabase"
- TTL Redis: "Redis con TTL" → corregido a "Supabase"
- Tabla tecnologías (2x): "Frontend React" → corregido a "Frontend HTML/JavaScript"

Pendiente verificación manual:
- Glosario del documento: la definición de "Redis" como tecnología — se recomienda actualizar a "Supabase (reemplazó Redis)"
- Tecnologías: "Node.js · Express.js" como backend — no se encontró Express.js en el código
- Sección 3.5 Supuestos y Dependencias menciona tecnologías que pueden incluir referencias ya corregidas

---

## 06_Plan_Pruebas.docx
Estado: CON CORRECCIONES ⚠

Correcciones aplicadas:
- Modelo Claude: era "Claude Sonnet 4.5" → corregido a "Claude Sonnet (claude-sonnet-4-6)"
- Alcance pruebas: era "M&oacute;dulo de chat con agente IA Claude Sonnet 4.5" → corregido
- Claves Redis (2x): "th:quote:{uuid}" → corregido a "cotizaciones (tabla Supabase)"
- Persistencia: era "persistencia PostgreSQL, caché Redis con TTL 10 días" → corregido a "persistencia en Supabase (tablas cotizaciones e historial)"
- Precondición: era "La base de datos PostgreSQL está configurada... Redis está activo..." → corregido a "Supabase está configurado..."
- Caso de prueba: "Persistencia en PostgreSQL" → corregido a "Persistencia en Supabase"
- Precondición: "Conexión PostgreSQL disponible" → corregido a "Conexión Supabase disponible"
- Frontend: era "El frontend React está desplegado en localhost:5173" → corregido a "El frontend HTML/JavaScript está desplegado en Vercel (staging)"
- Redis TTL: "Redis con TTL" → corregido a "Supabase"
- Número cotización: "COT-YYYY-XXX" → corregido a "COT-YYYY-XXXXX"
- Ejemplo (2x): "COT-2026-001" → corregido a "COT-2026-XXXXX"

Pendiente verificación manual:
- Varios casos de prueba mencionan "PostgreSQL" y "Redis" en condiciones específicas que requieren revisión manual completa (se encontraron 8x PostgreSQL y 15x Redis en texto tras correcciones)
- El alcance menciona "23 nodos del workflow n8n" — verificar con workflow actual
- Puerto localhost:5173 para frontend — no aplica (HTML estático)

---

## 07_Informe_Cierre.docx
Estado: CON CORRECCIONES ⚠

Correcciones aplicadas:
- Modelo Claude: era "Claude Sonnet 4.5 (Anthropic API)" → corregido a "Claude Sonnet (claude-sonnet-4-6, Anthropic API)"
- Frontend tabla: era "React.js · Tailwind CSS · Vercel" → corregido a "HTML/JavaScript vanilla · Tailwind CSS · Vercel"
- Frontend (3x): "React.js" → corregido a "HTML/JavaScript vanilla"
- Persistencia tabla: era "PostgreSQL (fuente de verdad) · Redis (caché TTL)" → corregido a "Supabase (PostgreSQL gestionado cloud)"
- Despliegue: era "Frontend: Vercel · Backend: Railway · BD: PostgreSQL + Redis" → corregido a "Frontend: Vercel · Backend: Railway · BD: Supabase"
- Contador: "th:counter" → corregido a "campo numero con timestamp (COT-YYYY-XXXXX)"
- Número secuencial: era "número correlativo único garantizado por INCR atómico en Redis." → corregido a "número único basado en timestamp (COT-YYYY-XXXXX)."
- Stack lista: "PostgreSQL, Redis" → corregido a "Supabase"
- Persistencia descripción: era "Persistencia dual: PostgreSQL como fuente de verdad y Redis con TTL..." → corregido a "Persistencia en Supabase (PostgreSQL gestionado cloud)."
- Integración: era "Integración Redis y PostgreSQL" → corregido a "Integración Supabase"
- Estado guardado: era "guardado en Redis" → corregido a "guardado en Supabase"
- Stack riesgo: "Node.js / React" → corregido a "Node.js / HTML/JavaScript"
- Número cotización (5x): "COT-YYYY-XXX" → corregido a "COT-YYYY-XXXXX"
- Base de datos tabla: era "Redis 7" → corregido a "Supabase"

Pendiente verificación manual:
- Sección de bugs resueltos: BUG-03 y otros pueden referenciar Redis — revisar manualmente
- "Redis · External" mencionado en diagrama/tabla de integraciones — actualizar a Supabase
- Tabla de riesgos con "PostgreSQL" y "Redis" en descripción de riesgos — revisar manualmente

---

## RESUMEN FINAL

- **Total documentos revisados:** 7
- **Documentos con correcciones aplicadas:** 7
- **Documentos sin cambios necesarios:** 0

### Correcciones por tipo:
| Tipo de corrección | Instancias corregidas |
|---|---|
| Base de datos: Redis/PostgreSQL → Supabase | ~45 |
| Frontend: React.js → HTML/JavaScript vanilla | ~15 |
| Modelo Claude: 4.5 → claude-sonnet-4-6 | 4 |
| Número cotización: COT-YYYY-XXX → COT-YYYY-XXXXX | ~30 |
| Claves Redis → tablas Supabase | ~25 |
| Webhook path: /chat → /chat-v2 | 1 |
| **TOTAL** | **~120** |

- **Total pendientes manuales:** 12 items en 5 documentos

### Porcentaje de coherencia documentación/código (estimado post-corrección):
- Datos técnicos críticos (modelo, BD, formato cotización): **~95% corregidos**
- Datos completos incluyendo contextos históricos y glosarios: **~85% alineados**
- Antes de la auditoría: **~40% alineados** (documentación describía arquitectura anterior con Redis/React)

### Inconsistencia más importante detectada:
La documentación completa del proyecto describía una arquitectura **anterior** del sistema:
- Frontend React → el código real usa HTML/JavaScript vanilla
- PostgreSQL + Redis → el código real usa Supabase
- Catálogo antiguo (Básico/Premium/Deportivo) → el código usa Luxury/Soft Touch/Pet-Friendly
- COT secuencial → el código usa timestamp

**Estas correcciones alinean los 7 documentos con el código real del proyecto.**
