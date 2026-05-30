# Trato Hecho 🌿

![Estado](https://img.shields.io/badge/Estado-En%20Producción-1D9E75)
![DuocUC](https://img.shields.io/badge/DuocUC-TPY1101-1F497D)
![HTML](https://img.shields.io/badge/Frontend-HTML%20%2B%20Tailwind-06B6D4)
![n8n](https://img.shields.io/badge/n8n-Self--Hosted-EA4B71)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase)
![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E?logo=railway)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?logo=vercel)
![Claude](https://img.shields.io/badge/IA-claude--sonnet--4--6-7C3AED)

Sistema de cotización automatizada con agente IA para **Césped Sintético SpA** (Melipilla, Chile).  
El cliente escribe en un chat, el agente calcula, genera y registra la cotización de forma instantánea.

---

## El problema que resuelve

- **2 a 4 días hábiles** de tiempo de respuesta por cotización manual → ahora tarda menos de 1 minuto
- **Metraje incorrecto** por medición visual del cliente → calculadora automática con margen técnico del 10%
- **Sin trazabilidad** de cotizaciones ni pagos → todo queda registrado en Supabase con número único `COT-YYYY-XXXXX`

---

## Arquitectura del sistema

```
[Cliente — Navegador / Smartphone]
          |
          ↓  POST https://main-production-38ed.up.railway.app/webhook/chat-v2
          |  Body: { message: string, sessionId: string }
          |
[Frontend HTML + Tailwind CSS — Vercel]
   chatbot.js · calculadora.html · panel de gestión (JWT)
          |
          ↓  Webhook n8n
          |
[Orquestador n8n — Railway Docker]
   Workflow: Trato Hecho - AI Agent v2.json
   claude-sonnet-4-6 · max_tokens: 1024
   Acciones: COTIZAR → PAGAR → CHAT
          |
          ├──→ [Claude API (Anthropic)]
          ├──→ [Supabase — PostgreSQL cloud]
          |     tablas: cotizaciones · historial
          ├──→ [MercadoPago — pago en línea]
          └──→ [Telegram + Gmail — notificaciones]
               chat_id: 8605918152 · aromero.madrid@gmail.com
```

---

## Stack tecnológico

| Capa | Tecnología | Detalles | Hosting |
|------|-----------|---------|---------|
| Frontend | HTML5 + JavaScript vanilla | Tailwind CSS · sin framework | Vercel |
| Chatbot | chatbot.js | sessionId en sessionStorage + localStorage | Vercel |
| Calculadora | calculadora.html | Math.ceil(m2 × 1.10) · 100% frontend | Vercel |
| Orquestador | n8n self-hosted | Docker · workflow AI Agent v2 | Railway |
| IA | Claude (Anthropic) | modelo: claude-sonnet-4-6 · 1024 tokens | API externa |
| Base de datos | Supabase | PostgreSQL cloud · tablas: cotizaciones, historial | Supabase cloud |
| Pagos | MercadoPago | Preference API · link de pago | API externa |
| Notificaciones | Telegram Bot + Gmail | nueva cotización y pago | API externas |
| Auth panel | JWT | 8h expiry · localStorage('trato_hecho_token') | — |

---

## Catálogo de productos

| Producto | Grosor | Precio/m² | Instalación |
|---------|--------|-----------|-------------|
| Luxury Emerald | 40mm | $28.500 CLP | +$4.500/m² |
| Soft Touch | 30mm | $22.900 CLP | +$4.500/m² |
| Pet-Friendly Turf | 35mm | $26.000 CLP | +$4.500/m² |
| Deportivos | variable | precio a cotizar | — |

**Fórmula:** `m2Final = Math.ceil(largo × ancho × 1.10)` — incluye 10% margen técnico de instalación.

---

## Estructura del repositorio

```
Trato_Hecho/
├── Producto/
│   ├── frontend/          # HTML + JS vanilla (index.html, chatbot.js, calculadora.html...)
│   ├── n8n/               # Workflow JSON + scripts de deploy (Python / PowerShell)
│   │   └── Trato Hecho - AI Agent v2.json   ← workflow de producción
│   └── config/
│       ├── config.js      # WEBHOOK_URL de producción
│       └── vercel.json    # config de deploy Vercel
├── Documentacion/
│   ├── word/              # 7 documentos .docx
│   ├── diagramas/         # 9 diagramas .drawio
│   ├── mockups/           # 6 mockups HTML estáticos
│   ├── historias-usuario/ # archivo .xlsx
│   ├── VERDAD_PROYECTO.md # fuente de verdad del código
│   └── AUDITORIA_DOCUMENTACION.md
├── Gestion/
│   ├── planificacion/     # Carta Gantt
│   └── riesgos/           # Matriz de riesgos
└── README.md
```

---

## Levantar el proyecto localmente

### Prerrequisitos

- Docker Desktop 4.x+
- Cuenta Supabase (gratuita)
- API key de Anthropic
- Node.js 18+ (opcional, para servir frontend)

### 1. Clonar

```bash
git clone https://github.com/Cristofer-SanMartin-Dev/Trato_Hecho.git
cd Trato_Hecho
```

### 2. Levantar n8n en Docker

```bash
docker run -d \
  --name trato_hecho_n8n \
  --restart unless-stopped \
  -p 127.0.0.1:5678:5678 \
  -v trato_hecho_n8n_data:/home/node/.n8n \
  n8io/n8n:latest
```

Acceder a n8n: **http://localhost:5678**

### 3. Importar el workflow

En n8n → Workflows → Import from file → seleccionar:
`Producto/n8n/Trato Hecho - AI Agent v2.json`

### 4. Configurar credenciales en n8n

Crear las credenciales en n8n para: Anthropic API, Supabase, Telegram, Gmail, MercadoPago.

### 5. Actualizar URL del webhook en el frontend

Editar `Producto/config/config.js`:

```js
const WEBHOOK_URL = 'http://localhost:5678/webhook/chat-v2';
```

### 6. Servir el frontend

```bash
# Con Python (desde Producto/frontend/)
python -m http.server 3000

# O con Node.js
npx serve . -p 3000
```

Abrir: **http://localhost:3000**

---

## Variables de entorno

```env
# n8n (se configuran directamente en n8n o via docker -e)
N8N_USER=
N8N_PASSWORD=

# APIs externas (se configuran como credenciales en n8n)
ANTHROPIC_API_KEY=
MERCADOPAGO_ACCESS_TOKEN=
FRONTEND_URL=

# Supabase (se configura como credencial en n8n)
# URL: https://enpzxntzphvezopbxbtx.supabase.co
# SUPABASE_ANON_KEY=
```

> No commitear credenciales reales. Ver `.env.example` en `Producto/config/`.

---

## Comandos útiles

```bash
# Ver logs de n8n en tiempo real
docker logs -f trato_hecho_n8n

# Reiniciar n8n
docker restart trato_hecho_n8n

# Re-desplegar workflow desde script
python Producto/n8n/fix_v2.py
```

---

## Equipo

| Nombre | Rol | Responsabilidad |
|--------|-----|----------------|
| Andrés Romero | Líder técnico | Arquitectura n8n · Railway · Integración IA |
| Manuel Carvajal | Frontend/UX | HTML · Calculadora · Panel de gestión |
| Cristofer San Martín | Backend/QA | Telegram · Gmail · MercadoPago · Pruebas |

---

## Documentación disponible

| # | Documento | Descripción |
|---|-----------|-------------|
| 1 | [Documentación Técnica Completa](Documentacion/word/01_Documentacion_Tecnica_Completa.docx) | Arquitectura, endpoints, flujo completo |
| 2 | [Manual de Instalación](Documentacion/word/02_Manual_Instalacion.docx) | Guía paso a paso para desplegar |
| 3 | [Manual de Usuario](Documentacion/word/03_Manual_Usuario.docx) | Cómo usar el chatbot y el panel |
| 4 | [Documentación Flujo n8n](Documentacion/word/04_Documentacion_Flujo_N8N.docx) | Nodos, ramas y lógica del workflow |
| 5 | [Especificación de Requerimientos SRS](Documentacion/word/05_Especificacion_Requerimientos_SRS.docx) | Requisitos funcionales y no funcionales |
| 6 | [Plan de Pruebas](Documentacion/word/06_Plan_Pruebas.docx) | Casos de prueba y resultados |
| 7 | [Informe de Cierre](Documentacion/word/07_Informe_Cierre.docx) | Resultados, métricas e indicadores |

---

## Estado EP2 — Evaluación 30 mayo 2026

| Requisito | Estado | Evidencia |
|-----------|--------|-----------|
| Historias de usuario con criterios de aceptación | ✅ | `Documentacion/historias-usuario/` |
| Mockups de interfaz (mín. 4 pantallas) | ✅ | `Documentacion/mockups/` — 6 mockups |
| Diagrama casos de uso UML | ✅ | `Documentacion/diagramas/Trato_Hecho_Casos_Uso.drawio` |
| Diagrama gestión de usuarios | ✅ | `Documentacion/diagramas/Trato_Hecho_Gestion_Usuarios.drawio` |
| 7 documentos Word actualizados | ✅ | `Documentacion/word/` |
| README.md profesional en GitHub | ✅ | Este archivo |
| Código en repositorio GitHub | ✅ | Branch `cs_cristofer` |
| Sistema desplegado en producción | ✅ | Vercel + Railway |
| Webhook funcional | ✅ | `POST /webhook/chat-v2` |
| Base de datos operativa | ✅ | Supabase — tablas `cotizaciones` y `historial` |
| Notificaciones activas | ✅ | Telegram + Gmail configurados |

---

## Licencia

MIT License · Proyecto académico DuocUC 2026 · TPY1101
