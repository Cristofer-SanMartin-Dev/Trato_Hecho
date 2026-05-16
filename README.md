# Trato Hecho — Manual de Instalación

> Manual de instalación y puesta en marcha para el proyecto Trato_Hecho.

---

## 1. Requisitos previos

Antes de instalar el proyecto, asegúrate de tener:

- Docker Desktop 4.x o superior
- Python 3.10+
- Node.js 18+ (opcional, para servir el frontend con `npx serve`)
- Git

---

## 2. Clonar el repositorio

```bash
git clone https://github.com/Cristofer-SanMartin-Dev/Trato_Hecho.git
cd Trato_Hecho
```

---

## 3. Levantar n8n en Docker

Ejecuta el siguiente comando para crear y ejecutar n8n:

```bash
docker run -d ^
  --name trato_hecho_n8n ^
  --restart unless-stopped ^
  -p 127.0.0.1:5678:5678 ^
  -v trato_hecho_n8n_data:/home/node/.n8n ^
  n8nio/n8n:latest
```

Si el contenedor ya existe, inicia n8n con:

```bash
docker start trato_hecho_n8n
```

Accede a la interfaz de n8n en: **http://localhost:5678**

---

## 4. Configurar n8n

### 4.1 Crear un usuario administrador

1. Abre `http://localhost:5678`.
2. Crea una cuenta de administrador.
3. Inicia sesión.

### 4.2 Generar API Key

1. En n8n, ve a `Settings → API`.
2. Crea una nueva API key.
3. Copia el valor generado.

---

## 5. Instalar dependencias Python

Desde la raíz del proyecto:

```bash
pip install requests
```

---

## 6. Configurar el proyecto

### 6.1 Actualizar `config.js`

Edita `config.js` y actualiza la URL del webhook de n8n:

```js
const WEBHOOK_URL = 'http://localhost:5678/webhook/chat-v2';
```

Si usas una URL pública (ngrok, Railway, etc.), reemplaza esta dirección por la URL pública.

### 6.2 Revisar `n8n/fix_v2.py`

En `n8n/fix_v2.py`, revisa que las siguientes variables apunten a tu instancia local de n8n:

- `API` — URL de la API de n8n
- `KEY` — API key generada en n8n
- `WF_ID` — ID del workflow en n8n (opcional según el script)

> No publiques estas credenciales.

---

## 7. Desplegar el workflow de n8n

Ejecuta el script desde la raíz del proyecto:

```bash
python n8n/fix_v2.py
```

### Resultado esperado

Deberías ver algo similar a:

```text
PUT OK | nodes: 10 | active: True
```

Esto indica que el workflow se actualizó correctamente en n8n.

---

## 8. Ejecutar el frontend

### Opción A — con Python

```bash
python -m http.server 3000
```

### Opción B — con Node.js

```bash
npx serve . -p 3000
```

Abrir en el navegador: **http://localhost:3000**

---

## 9. Probar el sistema

1. Abre `http://localhost:3000`.
2. Haz clic en el widget de chat.
3. Envía una solicitud de cotización.
4. Sigue el flujo para elegir producto, medidas e instalación.
5. Completa nombre, RUT y dirección.
6. Verifica que se muestre una cotización con número único.

---

## 10. Comandos útiles

```bash
# Ver logs de n8n en tiempo real
docker logs -f trato_hecho_n8n

# Reiniciar n8n
docker restart trato_hecho_n8n

# Detener n8n
docker stop trato_hecho_n8n

# Iniciar n8n
docker start trato_hecho_n8n

# Re-desplegar el workflow
python n8n/fix_v2.py
```

---

## 11. Troubleshooting

- n8n no responde: asegúrate de que Docker esté corriendo y el contenedor `trato_hecho_n8n` esté activo.
- El chat no conecta: revisa `WEBHOOK_URL` en `config.js`.
- El workflow no se despliega: verifica `n8n/fix_v2.py` y la API key.
- La cotización no se guarda: revisa la ejecución en n8n y la conexión a Supabase.

---

## 12. Notas finales

- No incluyas credenciales ni claves en el repositorio.
- Actualiza `config.js` cuando cambie la URL del backend.
- Usa `docker ps` para ver el estado del contenedor n8n.
- Si necesitas reinstalar n8n, elimina el contenedor y vuelve a ejecutar el `docker run`.

---

## 13. Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 14. Contribución

¡Las contribuciones son bienvenidas! Para contribuir:

1. Haz un fork del repositorio.
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Añade nueva funcionalidad'`).
4. Push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

Para reportar bugs o solicitar features, usa los [Issues](https://github.com/Cristofer-SanMartin-Dev/Trato_Hecho/issues) de GitHub.

Asegúrate de seguir las buenas prácticas: no incluir credenciales, probar cambios localmente y documentar modificaciones.
