# Estructura del Proyecto Trato Hecho

Esta carpeta contiene el código organizado del proyecto, dividido en las siguientes secciones:

## 📁 Estructura

### `/frontend`
Contiene todos los archivos del frontend:
- **Páginas HTML:** `index.html`, `calculadora.html`, `contacto.html`, `documento.html`, `insumos.html`, `jardines.html`, `pasto-deportivo.html`
- **Scripts JavaScript:** `chatbot.js`, `apply.js`, `apply2.js`, `replace.js`, `update_*.js`
- **Servidor local:** `serve.py`
- **Recursos:** `chatbot-avatar.png`, `heros.txt`

### `/scripts`
Scripts de automatización y utilidad:
- Scripts de actualización: `update_chat.py`, `update_chatbot.py`, `update_n8n.py`, `update_nav.py`, `update_ngrok.py`
- Scripts de procesamiento: `apply_*.py`, `extract_*.py`, `fix_*.py`, `patch_*.py`
- Scripts de utilidad: `add_seo.py`, `build_new_workflow.py`, `check_*.py`, `deploy_n8n.py`, `generar_docx.py`, etc.

### `/n8n`
Workflows y scripts para n8n:
- Archivos de workflow: `Trato Hecho - AI Agent v2.json`, `Trato Hecho - Chat Agent (2).json`
- Backups: `workflow_backup.json`, `workflow_current.json`
- Scripts de deployment: `deploy_*.py`, `deploy_*.ps1`
- Scripts de diagnóstico: `check_*.ps1`, `diag_*.py`
- Utilidades: `fix_*.py`, `update_*.py`, `test_*.py`, etc.

### `/config`
Archivos de configuración:
- `config.js` - Configuración del proyecto
- `vercel.json` - Configuración de Vercel
- `.env.example` - Ejemplo de variables de entorno

## 🚀 Uso

Para ejecutar la aplicación:
```bash
cd frontend
python serve.py
```

Para ejecutar scripts de actualización:
```bash
python scripts/update_n8n.py
```

Para trabajar con n8n workflows:
```bash
cd n8n
# Ver archivos de workflow disponibles
```

## 📝 Notas
- Los scripts Python están organizados por función
- Los workflows de n8n están en la carpeta dedicada con sus scripts de soporte
- La configuración centralizada está en `/config`
