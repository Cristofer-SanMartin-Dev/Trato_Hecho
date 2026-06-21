# tools/_archive/

Scripts de un solo uso usados durante el desarrollo inicial de Trato Hecho.

Están archivados aquí para referencia histórica. **No ejecutar directamente.**

- Los scripts de deploy/fix de n8n (`n8n_deploy_*.py`, `n8n_fix_*.ps1`, etc.) ya no son necesarios:
  el workflow activo es `n8n/Trato Hecho - AI Agent v2.json`.
- Los scripts de saneamiento (`sanitize_secrets.js`, `fix_*.js`) ya se ejecutaron;
  sus cambios están integrados en el código.
- Las claves hardcodeadas que existían en estos scripts han sido reemplazadas
  por referencias a variables de entorno (`os.environ.get(...)`, `$env:VAR`).

Para volver a desplegar el workflow, importar directamente el JSON en n8n
y configurar las variables de entorno indicadas en `.env.example`.
