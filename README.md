# Trato Hecho — Chatbot de Cotizaciones

> Guía técnica para levantar el sistema completo en local.

---

## Descripción

Sistema de chatbot para Césped Sintético ARM. El chatbot **Queno** atiende clientes, calcula precios, genera cotizaciones formales y las guarda en Supabase. Incluye calculadora de metraje integrada en el chat.

**Stack:**
- Frontend: HTML + Tailwind CSS + JS vanilla (`index.html`)
- Backend: n8n (Docker) con agente Claude AI
- Base de datos: Supabase (cotizaciones)
- IA: Anthropic Claude Sonnet 4.5

---

## Requisitos previos

Instalar en el equipo antes de continuar:

| Herramienta | Versión mínima | Descarga |
|---|---|---|
| Docker Desktop | 4.x | https://www.docker.com/products/docker-desktop |
| Python | 3.10+ | https://www.python.org/downloads |
| Node.js | 18+ | https://nodejs.org |
| Git | cualquiera | https://git-scm.com |

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/Cristofer-SanMartin-Dev/Trato_Hecho.git
cd Trato_Hecho
git checkout desarrollo
```

---

## 2. Levantar n8n con Docker

Ejecutar **una sola vez** para crear el contenedor:

```bash
docker run -d ^
  --name trato_hecho_n8n ^
  --restart unless-stopped ^
  -p 127.0.0.1:5678:5678 ^
  -v trato_hecho_n8n_data:/home/node/.n8n ^
  n8nio/n8n:latest
```

Verificar que está corriendo:

```bash
docker ps
# Debe aparecer: trato_hecho_n8n   Up X minutes   127.0.0.1:5678->5678/tcp
```

Si el contenedor ya existe de una sesión anterior, solo iniciarlo:

```bash
docker start trato_hecho_n8n
```

n8n queda accesible en: **http://localhost:5678**

---

## 3. Configurar n8n (primera vez)

1. Abrir http://localhost:5678 en el navegador
2. Crear una cuenta de administrador (email + contraseña cualquiera)
3. Ir a **Settings → n8n API → Create API key**
4. Copiar esa API key — la necesitarás en el siguiente paso

---

## 4. Instalar dependencias Python

```bash
pip install requests
```

---

## 5. Configurar credenciales en fix_v2.py

Abrir `n8n/fix_v2.py` y actualizar estas variables al inicio del archivo:

```python
N8N_BASE   = "http://localhost:5678"
N8N_API_KEY = "TU_API_KEY_DE_N8N"   # La que generaste en el paso 3
```

Las credenciales de Supabase y Anthropic ya están configuradas en el archivo.
Pedir las API keys al equipo de desarrollo si necesitas actualizarlas.

> **IMPORTANTE:** Nunca subas API keys a GitHub.

---

## 6. Desplegar el workflow en n8n

Desde la carpeta raíz del proyecto:

```bash
python n8n/fix_v2.py
```

Salida esperada:

```
Got workflow: Trato Hecho - AI Agent v2 | active: True
✓ Agent: system prompt updated
✓ LLM: typeVersion=1.3, model=claude-sonnet-4-5
✓ Tool calcular_precio: sports prices added
✓ Tool guardar_cotizacion: simplified (no HTTP in sandbox)
✓ Tool generar_pago: fixed (no fetch in sandbox)
✓ Guardar en Supabase: code updated (existing node)
✓ Connections: AI Agent → Guardar en Supabase → Responder Webhook

PUT OK | nodes: 10 | active: True
```

Si aparece `PUT OK` el backend está listo.

---

## 7. Levantar el frontend

Desde la carpeta raíz del proyecto:

```bash
# Opción A — Python (recomendado)
python -m http.server 3000

# Opción B — Node.js
npx serve . -p 3000
```

Abrir en el navegador: **http://localhost:3000**

---

## 8. Probar el sistema

**Flujo completo de cotización:**
1. Abrir http://localhost:3000
2. Hacer clic en el ícono del chat (abajo a la derecha)
3. Escribir: `Quiero cotizar Soft Touch 30mm`
4. El bot preguntará si conoces las medidas
5. Seguir el flujo hasta ingresar nombre, RUT y dirección
6. Al final debe aparecer una tarjeta verde con el número de cotización

**Probar la calculadora de metraje:**
1. Cuando el bot pregunte por las medidas, responder: `no sé las medidas`
2. Debe aparecer una calculadora verde dentro del chat
3. Ingresar largo y ancho → presionar "✅ Usar estos metros"
4. El mensaje se envía automáticamente y el bot continúa

---

## Arquitectura del sistema

```
Cliente (localhost:3000)
        │
        │  POST /webhook/chat-v2
        ▼
n8n (localhost:5678)
   ├── Webhook Chat
   ├── Extraer Input
   ├── AI Agent (Claude Sonnet 4.5)
   │     ├── Tool: calcular_precio
   │     ├── Tool: guardar_cotizacion
   │     └── Tool: generar_pago
   ├── Guardar en Supabase
   └── Responder Webhook
        │
        ▼
Supabase (tabla: cotizaciones)
  columnas: id, numero_cotizacion, nombre, rut, direccion,
            producto, m2, precio_unitario, con_instalacion, total
```

---

## Comandos útiles

```bash
# Ver logs de n8n en tiempo real
docker logs -f trato_hecho_n8n

# Reiniciar n8n
docker restart trato_hecho_n8n

# Detener n8n
docker stop trato_hecho_n8n

# Volver a iniciar n8n
docker start trato_hecho_n8n

# Re-desplegar cambios del workflow (después de editar fix_v2.py)
python n8n/fix_v2.py
```

---

## Problemas frecuentes

| Error | Causa | Solución |
|---|---|---|
| `Connection refused` en el chat | n8n no está corriendo | `docker start trato_hecho_n8n` |
| `PUT 400` al correr fix_v2.py | API key incorrecta o expirada | Regenerar en n8n Settings → API |
| La calculadora no aparece | Caché del navegador | Recargar con Ctrl+Shift+R |
| Cotización no se guarda en Supabase | Error en nodo "Guardar en Supabase" | Ver n8n → Executions → último error |
| El bot no responde | Créditos de Anthropic agotados | Verificar en console.anthropic.com |
| `docker: name already in use` | El contenedor ya existe | Usar `docker start trato_hecho_n8n` |

---

## Contacto

Para obtener las API keys (Anthropic, Supabase) o acceso al proyecto, contactar al equipo de desarrollo.
