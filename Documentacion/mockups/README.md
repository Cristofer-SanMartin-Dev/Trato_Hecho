# Mockups — Trato Hecho

Mockups estáticos HTML. Datos representativos del sistema real.

## Abrir

Abrir directamente en el navegador (doble clic sobre el archivo `.html`).

No requieren servidor, build ni dependencias.

## Tabla de mockups

| # | Archivo | Pantalla | Componente / Sección | Endpoint relacionado |
|---|---------|----------|----------------------|----------------------|
| 1 | [01_pagina_principal.html](01_pagina_principal.html) | Landing page con catálogo de productos | Página principal + FAB chat | — (estático) |
| 2 | [02_chat_conversacion.html](02_chat_conversacion.html) | Chat widget abierto — flujo de cotización | `chatbot.js` — widget flotante | `POST /webhook/chat-v2` |
| 3 | [03_quote_card.html](03_quote_card.html) | QuoteCard generada dentro del chat | `chatbot.js` — render de cotización | `POST /webhook/chat-v2` (acción COTIZAR) |
| 4 | [04_calculadora.html](04_calculadora.html) | Calculadora interactiva de m² | `calculadora.html` — cálculo frontend | — (100% JavaScript local) |
| 5 | [05_panel_login.html](05_panel_login.html) | Panel de gestión — login JWT | Autenticación panel interno | `POST /api/auth/login` |
| 6 | [06_panel_dashboard.html](06_panel_dashboard.html) | Panel de gestión — dashboard cotizaciones | Vista de gestión del negocio | Supabase tabla `cotizaciones` |

## Notas técnicas

- Fórmula de cálculo real: `Math.ceil(largo × ancho × 1.10)`
- Precios reales: Luxury Emerald $28.500/m², Soft Touch $22.900/m², Pet-Friendly $26.000/m²
- Instalación: +$4.500/m² (solo productos residenciales)
- Número de cotización: formato `COT-YYYY-XXXXX` (últimos 5 dígitos de `Date.now()`)
- Webhook producción: `https://main-production-38ed.up.railway.app/webhook/chat-v2`
- Colores del sistema: Azul #1F497D · Azul medio #2E75B6 · Verde #1D9E75
