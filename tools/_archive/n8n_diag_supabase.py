import os
"""Diagnóstico: consulta Supabase directamente para verificar la query."""
import urllib.request, json

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

def sb_get(path):
    req = urllib.request.Request(
        SUPABASE_URL + path,
        headers={'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# 1. Ver todos los números disponibles
print('=== Cotizaciones en Supabase ===')
rows = sb_get('/rest/v1/cotizaciones?select=id,numero,nombre,total&order=id.asc&limit=20')
for r in rows:
    print(f'  id={r["id"]} numero={r["numero"]!r} nombre={r.get("nombre","?")} total={r.get("total","?")}')

# 2. Buscar COT-2026-93240 exacto
print('\n=== Query exacta: numero=eq.COT-2026-93240 ===')
result = sb_get('/rest/v1/cotizaciones?numero=eq.COT-2026-93240&limit=1')
print('Resultado:', result)

# 3. Ver columnas exactas de un registro
if rows:
    print('\n=== Columnas del primer registro ===')
    print(json.dumps(rows[0], ensure_ascii=False, indent=2))
