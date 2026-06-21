/**
 * sanitize_secrets.js — reemplaza secretos hardcodeados por referencias a env vars
 * Uso: node tools/sanitize_secrets.js
 * Borrar este script después de ejecutarlo (o moverlo a tools/_archive/).
 */
const fs   = require('fs');
const path = require('path');

const N8N_KEY  = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw';
const SUP_URL  = 'https://enpzxntzphvezopbxbtx.supabase.co';
const SUP_KEY  = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVucHp4bnR6cGh2ZXpvcGJ4YnR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc3MTEzMDUsImV4cCI6MjA5MzI4NzMwNX0.kdT61HJFXFiDXPQUqwZivOmjDFJO3aoY7XETf_LoZQ4';
const MP_TOKEN = 'TEST-3130883879758417-040519-bf1c10ceecc464549aa07169a7d118a3-93809061';

// ── Python ────────────────────────────────────────────────────────────────────
function sanitizePy(content) {
  let c = content;
  // n8n API key (puede aparecer entre comillas simples o dobles)
  c = c.split("'" + N8N_KEY + "'").join("os.environ.get('N8N_API_KEY', '')");
  c = c.split('"' + N8N_KEY + '"').join("os.environ.get('N8N_API_KEY', '')");
  // Supabase URL
  c = c.split("'" + SUP_URL + "'").join("os.environ.get('SUPABASE_URL', '')");
  c = c.split('"' + SUP_URL + '"').join("os.environ.get('SUPABASE_URL', '')");
  // Supabase key
  c = c.split("'" + SUP_KEY + "'").join("os.environ.get('SUPABASE_KEY', '')");
  c = c.split('"' + SUP_KEY + '"').join("os.environ.get('SUPABASE_KEY', '')");
  // MercadoPago token
  c = c.split("'" + MP_TOKEN + "'").join("os.environ.get('MERCADOPAGO_ACCESS_TOKEN', '')");
  c = c.split('"' + MP_TOKEN + '"').join("os.environ.get('MERCADOPAGO_ACCESS_TOKEN', '')");
  // Agregar 'import os' si aún no está y el archivo usa os.environ
  if (c.includes("os.environ") && !c.includes("import os")) {
    c = "import os\n" + c;
  }
  return c;
}

// ── PowerShell ────────────────────────────────────────────────────────────────
function sanitizePs1(content) {
  let c = content;
  c = c.split('"' + N8N_KEY + '"').join('$env:N8N_API_KEY');
  c = c.split("'" + N8N_KEY + "'").join('$env:N8N_API_KEY');
  c = c.split('"' + SUP_URL + '"').join('$env:SUPABASE_URL');
  c = c.split("'" + SUP_URL + "'").join('$env:SUPABASE_URL');
  c = c.split('"' + SUP_KEY + '"').join('$env:SUPABASE_KEY');
  c = c.split("'" + SUP_KEY + "'").join('$env:SUPABASE_KEY');
  c = c.split('"' + MP_TOKEN + '"').join('$env:MERCADOPAGO_ACCESS_TOKEN');
  c = c.split("'" + MP_TOKEN + "'").join('$env:MERCADOPAGO_ACCESS_TOKEN');
  return c;
}

// ── Workflow activo (jsCode usa $env en n8n) ──────────────────────────────────
function sanitizeActiveWorkflow(content) {
  let c = content;
  c = c.split(SUP_URL).join('$env.SUPABASE_URL');
  c = c.split(SUP_KEY).join('$env.SUPABASE_KEY');
  c = c.split(MP_TOKEN).join('$env.MERCADOPAGO_ACCESS_TOKEN');
  c = c.split(N8N_KEY).join('[REDACTED-USE-ENV]');
  return c;
}

// ── JSONs de archivo (redact completo) ───────────────────────────────────────
function sanitizeArchiveJson(content) {
  let c = content;
  c = c.split(N8N_KEY).join('[REDACTED-USE-ENV]');
  c = c.split(SUP_URL).join('[REDACTED-USE-ENV]');
  c = c.split(SUP_KEY).join('[REDACTED-USE-ENV]');
  c = c.split(MP_TOKEN).join('[REDACTED-USE-ENV]');
  return c;
}

let changed = 0;

function processFile(filePath, fn) {
  try {
    const orig = fs.readFileSync(filePath, 'utf8');
    const updated = fn(orig);
    if (orig !== updated) {
      fs.writeFileSync(filePath, updated, 'utf8');
      console.log('  FIXED:', filePath);
      changed++;
    }
  } catch (e) {
    console.error('  ERROR:', filePath, e.message);
  }
}

// Python files
const pyFiles = [
  ...fs.readdirSync('.').filter(f => f.endsWith('.py')),
  ...fs.readdirSync('n8n').filter(f => f.endsWith('.py')).map(f => 'n8n/' + f),
];
console.log(`\n── Python (${pyFiles.length} archivos) ──`);
pyFiles.forEach(f => processFile(f, sanitizePy));

// PowerShell files
const ps1Roots = fs.readdirSync('.').filter(f => f.endsWith('.ps1'));
const ps1N8n   = fs.existsSync('n8n') ? fs.readdirSync('n8n').filter(f => f.endsWith('.ps1')).map(f => 'n8n/' + f) : [];
const ps1Files = [...ps1Roots, ...ps1N8n];
console.log(`\n── PowerShell (${ps1Files.length} archivos) ──`);
ps1Files.forEach(f => processFile(f, sanitizePs1));

// Active workflow
const activeWf = 'n8n/Trato Hecho - AI Agent v2.json';
console.log('\n── Workflow activo ──');
processFile(activeWf, sanitizeActiveWorkflow);

// Archive JSONs
const archiveJsons = fs.readdirSync('n8n')
  .filter(f => f.endsWith('.json') && f !== 'Trato Hecho - AI Agent v2.json')
  .map(f => 'n8n/' + f);
console.log(`\n── JSONs de archivo (${archiveJsons.length}) ──`);
archiveJsons.forEach(f => processFile(f, sanitizeArchiveJson));

console.log(`\n✅ Total archivos modificados: ${changed}`);
