# Documentación Técnica — Trato Hecho

> Documentación técnica del proyecto Trato_Hecho.

---

## 1. Descripción del sistema

Trato_Hecho es un producto que une un frontend estático con un flujo de automatización n8n y un servicio de IA para generar cotizaciones de césped sintético.

El sistema permite:
- Recibir solicitudes de cotización por chat.
- Interpretar el producto solicitado y las medidas del cliente.
- Calcular precios con margen técnico y opcional de instalación.
- Guardar cotizaciones formales en Supabase.
- Devolver una respuesta final en el chat con un número de cotización.

---

## 2. Componentes principales

### 2.1 Frontend
- `index.html`: página principal y punto de entrada del sitio.
- `calculadora.html`, `documento.html`, `contacto.html`: páginas adicionales con el widget de chat.
- `chatbot.js`: controla el widget de chat, la interfaz de usuario y la comunicación con n8n.
- `config.js`: configuración del webhook de n8n.

### 2.2 Backend / n8n
- `n8n/Trato Hecho - Chat Agent (2).json`: workflow exportado de n8n.
- `n8n/fix_v2.py`: script de despliegue y parcheo del workflow en n8n.
- `build_new_workflow.py`: reconstruye el workflow con nodos Supabase, Claude y lógica de conversación.
- `deploy_n8n.py`: despliega un workflow usando el ID de n8n.

### 2.3 Persistencia
- Supabase: tabla `cotizaciones` utilizada para persistir cotizaciones y consultarlas desde el flujo.

### 2.4 IA
- Claude AI (Anthropic) se usa para procesar la conversación, identificar intenciones y generar respuestas estructuradas.

---

## 3. Flujo de datos

1. El frontend envía mensajes al webhook de n8n.
2. n8n procesa el input y construye el prompt para Claude.
3. Claude responde con acciones, cálculos y contenido para el usuario.
4. n8n guarda la cotización en Supabase.
5. El resultado regresa al frontend y se muestra al usuario.

---

## 4. Arquitectura del workflow n8n

### Nodos clave
- Webhook: recibe los mensajes del frontend.
- Código/función de extracción: normaliza el input del cliente.
- Prompt builder: construye el prompt para Claude.
- Llamada a Claude API: envía el prompt y recibe la respuesta.
- Parseo de respuesta: extrae datos relevantes.
- Guardar en Supabase: persiste la cotización.
- Responder al webhook: envía la respuesta final al cliente.

---

## 5. Arquitectura del frontend

### `chatbot.js`
- Maneja la apertura/cierre del chat.
- Construye los mensajes de usuario.
- Envía solicitudes al endpoint configurado en `config.js`.
- Interpreta respuestas de n8n y muestra el contenido en la interfaz.

### Interacción del usuario
- Si el usuario no conoce las medidas, el bot despliega una calculadora.
- Si el usuario proporciona largo y ancho, calcula m² internamente.
- El bot solicita nombre, RUT y dirección antes de generar la cotización formal.

---

## 6. Configuración del ambiente

### n8n
- Debe correr en Docker y estar accesible en `http://localhost:5678`.
- Requiere una API key para que `n8n/fix_v2.py` pueda desplegar el workflow.

### Supabase
- El proyecto depende de un endpoint Supabase configurado en los scripts del workflow.
- La tabla `cotizaciones` debe existir y aceptar datos de cotización.

### Claude
- El workflow usa Claude Sonnet 4.5.
- La configuración del modelo y el prompt se define en `n8n/fix_v2.py` y `build_new_workflow.py`.

---

## 7. Variables y archivos de configuración

- `config.js`: URL de webhook para el frontend.
- `n8n/fix_v2.py`: URL de API, API key y workflow ID de n8n.
- `build_new_workflow.py`: URL de Supabase y estructura de nodos.
- `deploy_n8n.py`: despliegue usando el ID del workflow.

---

## 8. Seguridad

### Manejo de credenciales
- Las API keys de n8n, Supabase y Anthropic se almacenan en variables de entorno o archivos locales (no versionados).
- Nunca subas credenciales a GitHub. Usa `.gitignore` para excluir archivos sensibles.
- En producción, usa servicios como Azure Key Vault o AWS Secrets Manager para credenciales.

### Encriptación de datos
- Las comunicaciones entre frontend y n8n usan HTTPS en producción.
- Los datos de cotizaciones en Supabase están encriptados en reposo.
- El prompt de Claude no incluye datos sensibles; solo información de cotización.

### Mejores prácticas
- Rotar API keys periódicamente.
- Limitar permisos de Supabase a solo lectura/escritura en tabla `cotizaciones`.
- Monitorear logs de n8n para detectar accesos no autorizados.

---

## 9. Rendimiento y escalabilidad

### Límites de Claude AI
- Claude Sonnet 4.5 tiene límites de tokens por minuto (TPM) y requests por minuto (RPM).
- Para alto volumen, considera rate limiting en n8n o usar Claude con mayor capacidad.
- El prompt actual es optimizado para respuestas rápidas (< 500 tokens).

### Optimización de n8n
- El workflow es ligero: ~10 nodos, ejecución típica < 5 segundos.
- Para escalabilidad, usa n8n en cluster o despliega en Kubernetes.
- Monitorea uso de CPU/memoria en Docker.

### Escalabilidad general
- Frontend estático: escala bien con CDN (e.g., Vercel, Netlify).
- Supabase maneja hasta 50k requests/día gratis; escala automáticamente.
- Para >1000 cotizaciones/día, considera caching o optimización de queries.

---

## 10. Esquemas de datos

### Tabla `cotizaciones` en Supabase
```sql
CREATE TABLE cotizaciones (
  id SERIAL PRIMARY KEY,
  numero VARCHAR(20) UNIQUE NOT NULL,  -- e.g., 'COT-2024-0001'
  session_id VARCHAR(50),               -- ID de sesión de chat
  nombre VARCHAR(100) NOT NULL,
  rut VARCHAR(20) NOT NULL,
  direccion TEXT NOT NULL,
  producto VARCHAR(100) NOT NULL,
  m2 DECIMAL(10,2) NOT NULL,
  precio_unitario DECIMAL(10,2),
  instalacion BOOLEAN DEFAULT FALSE,
  total DECIMAL(10,2) NOT NULL,
  estado VARCHAR(20) DEFAULT 'pendiente',  -- pendiente, aprobado, rechazado
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Índices recomendados
- `CREATE INDEX idx_session_id ON cotizaciones(session_id);`
- `CREATE INDEX idx_numero ON cotizaciones(numero);`

### API Endpoints de Supabase
- `POST /rest/v1/cotizaciones`: Crear nueva cotización.
- `GET /rest/v1/cotizaciones?session_id=eq.{session_id}`: Obtener historial por sesión.

---

## 11. Diagrama de flujo de datos

```
Usuario (Navegador)
    │
    ▼
Frontend (index.html + chatbot.js)
    │ POST /webhook/chat-v2
    ▼
n8n Workflow
├── Webhook Node → Extraer Input
├── Construir Prompt → Llamar Claude API
├── Parsear Respuesta → Guardar en Supabase
└── Responder Webhook
    │
    ▼
Supabase (Tabla: cotizaciones)
    │
    ▼
Respuesta al Usuario
```

---

## 12. Glosario de términos

- `Webhook`: Punto de entrada en n8n para recibir solicitudes de chat.
- `Workflow`: Secuencia de nodos en n8n que procesa la conversación.
- `Supabase`: Servicio de base de datos y API REST.
- `Claude`: Modelo de IA responsable del procesamiento conversacional.
- `Cotización`: Registro formal guardado en Supabase con número único.
