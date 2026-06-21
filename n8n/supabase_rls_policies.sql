-- ============================================================
--  TRATO HECHO — Row Level Security (RLS) para Supabase
--  Ejecutar en: Supabase Dashboard → SQL Editor
--
--  Estrategia:
--    - El rol anon NO tiene acceso (el chatbot usa service_role en n8n).
--    - El rol authenticated tampoco accede (no hay login de usuarios finales).
--    - Solo service_role (clave secreta de n8n) puede leer/escribir.
--
--  IMPORTANTE: en n8n, reemplazar la anon key por la service_role key.
--  La service_role key está en: Supabase → Settings → API → service_role.
--  Nunca la expongas en el frontend ni en archivos públicos.
-- ============================================================

-- ── 1. HABILITAR RLS EN TODAS LAS TABLAS ─────────────────────────────────────

ALTER TABLE cotizaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE venta        ENABLE ROW LEVEL SECURITY;
ALTER TABLE historial    ENABLE ROW LEVEL SECURITY;

-- ── 2. REVOCAR ACCESO PUBLIC (anon + authenticated) ──────────────────────────

-- cotizaciones
REVOKE ALL ON cotizaciones FROM anon;
REVOKE ALL ON cotizaciones FROM authenticated;

-- venta
REVOKE ALL ON venta FROM anon;
REVOKE ALL ON venta FROM authenticated;

-- historial
REVOKE ALL ON historial FROM anon;
REVOKE ALL ON historial FROM authenticated;

-- ── 3. ELIMINAR POLÍTICAS EXISTENTES (si las hay) ────────────────────────────

DROP POLICY IF EXISTS "deny_anon_cotizaciones"   ON cotizaciones;
DROP POLICY IF EXISTS "deny_anon_venta"          ON venta;
DROP POLICY IF EXISTS "deny_anon_historial"      ON historial;
DROP POLICY IF EXISTS "allow_service_cotizaciones" ON cotizaciones;
DROP POLICY IF EXISTS "allow_service_venta"        ON venta;
DROP POLICY IF EXISTS "allow_service_historial"    ON historial;

-- ── 4. POLÍTICAS: BLOQUEAR acceso anon explícitamente ────────────────────────
--  Con RLS habilitado y sin política permisiva, todo está bloqueado por defecto.
--  Estas políticas DENY son redundantes pero documentan la intención.

CREATE POLICY "deny_anon_cotizaciones"
  ON cotizaciones
  FOR ALL
  TO anon
  USING (false);

CREATE POLICY "deny_anon_venta"
  ON venta
  FOR ALL
  TO anon
  USING (false);

CREATE POLICY "deny_anon_historial"
  ON historial
  FOR ALL
  TO anon
  USING (false);

-- ── 5. NOTA SOBRE service_role ────────────────────────────────────────────────
--  El rol service_role bypasea RLS por diseño en Supabase.
--  No se necesita política explícita para él.
--
--  Para usar service_role en n8n:
--    1. Ir a Supabase → Settings → API → service_role secret
--    2. En n8n, configurar la variable de entorno:
--         SUPABASE_KEY=<service_role key>
--    3. Nunca incluir la service_role key en el frontend ni en .env.example.

-- ── 6. VERIFICACIÓN ───────────────────────────────────────────────────────────
--  Ejecutar después de aplicar las políticas:

SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE tablename IN ('cotizaciones', 'venta', 'historial');

-- Resultado esperado: rowsecurity = true para las 3 tablas.
