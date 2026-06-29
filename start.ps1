# ============================================================
#  TRATO HECHO — Iniciar todos los servicios
# ============================================================

$N8N_CONTAINER  = "sanos-n8n"
$N8N_URL        = "http://localhost:5678"
$WF_ID          = "SsuEREJAEGWy3jm0"
$N8N_EMAIL      = "admin@sanosysalvos.local"
$N8N_PASSWORD   = "TratoHecho2024!"
$FRONTEND_PORT  = 3000
$SCRIPT_DIR     = $PSScriptRoot
$CONFIG_FILE    = Join-Path $SCRIPT_DIR "config.js"
$WEBHOOK_LOCAL  = "http://localhost:5678/webhook/chat-v2"

Clear-Host
Write-Host ""
Write-Host "  ==========================================" -ForegroundColor Cyan
Write-Host "       TRATO HECHO - INICIANDO SISTEMA      " -ForegroundColor White
Write-Host "  ==========================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Docker / n8n ──────────────────────────────────────────
Write-Host "  [1/4] Verificando contenedor n8n..." -ForegroundColor Yellow

$status = docker inspect --format '{{.State.Status}}' $N8N_CONTAINER 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERR] Contenedor '$N8N_CONTAINER' no existe." -ForegroundColor Red
    Read-Host "`n  Presiona Enter para cerrar"
    exit 1
}

if ($status -ne "running") {
    Write-Host "  [~~]  Iniciando contenedor..." -ForegroundColor Yellow
    docker start $N8N_CONTAINER | Out-Null
}

# Esperar que n8n responda
$maxWait = 60; $elapsed = 0; $ready = $false
while ($elapsed -lt $maxWait) {
    try {
        $r = Invoke-WebRequest -Uri "$N8N_URL/healthz" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 2; $elapsed += 2
    Write-Host "  [~~]  Esperando n8n... ($elapsed/$maxWait s)" -ForegroundColor DarkGray
}

if (-not $ready) {
    Write-Host "  [ERR] n8n no respondio en $maxWait s." -ForegroundColor Red
    Read-Host "`n  Presiona Enter para cerrar"
    exit 1
}
Write-Host "  [OK]  n8n listo." -ForegroundColor Green

# ── 2. Activar workflow via Node en el contenedor ────────────
Write-Host "  [2/4] Activando workflow del agente..." -ForegroundColor Yellow

$nodeScript = @"
const http = require('http');
function req(opts, body) {
  return new Promise((res, rej) => {
    const r = http.request(opts, rr => {
      let d = '';
      rr.on('data', c => d += c);
      rr.on('end', () => res({ status: rr.statusCode, headers: rr.headers, body: d }));
    });
    r.on('error', rej);
    if (body) r.write(body);
    r.end();
  });
}
async function main() {
  const loginBody = JSON.stringify({ emailOrLdapLoginId: '$N8N_EMAIL', password: '$N8N_PASSWORD' });
  const lr = await req({ hostname:'localhost',port:5678,path:'/rest/login',method:'POST',
    headers:{'Content-Type':'application/json','Content-Length':Buffer.byteLength(loginBody)} }, loginBody);
  if (lr.status !== 200) { console.log('ERROR:Login fallido'); process.exit(1); }
  const sc = lr.headers['set-cookie'];
  const cookie = Array.isArray(sc) ? sc.map(c=>c.split(';')[0]).join('; ') : sc.split(';')[0];
  const wr = await req({ hostname:'localhost',port:5678,path:'/rest/workflows/$WF_ID',method:'GET',
    headers:{Cookie:cookie} });
  const wf = (JSON.parse(wr.body).data || JSON.parse(wr.body));
  if (wf.active) { console.log('STATUS:active'); return; }
  const ab = JSON.stringify({ versionId: wf.versionId });
  const ar = await req({ hostname:'localhost',port:5678,path:'/rest/workflows/$WF_ID/activate',method:'POST',
    headers:{'Content-Type':'application/json','Content-Length':Buffer.byteLength(ab),Cookie:cookie} }, ab);
  const ad = JSON.parse(ar.body);
  console.log('STATUS:' + ((ad.data||ad).active ? 'activated' : 'error'));
}
main().catch(e => { console.log('ERROR:'+e.message); process.exit(1); });
"@

$result = $nodeScript | docker exec -i $N8N_CONTAINER node 2>&1
$statusLine = $result | Where-Object { $_ -match '^STATUS:|^ERROR:' } | Select-Object -First 1

switch -Wildcard ($statusLine) {
    "STATUS:active"    { Write-Host "  [OK]  Agente ya estaba activo." -ForegroundColor Green }
    "STATUS:activated" { Write-Host "  [OK]  Agente activado." -ForegroundColor Green }
    "STATUS:error"     { Write-Host "  [!]   No se pudo activar el agente." -ForegroundColor Yellow }
    "ERROR:*"          { Write-Host "  [ERR] $($statusLine.Substring(6))" -ForegroundColor Red }
    default            { Write-Host "  [OK]  Agente procesado." -ForegroundColor Green }
}

# ── 3. Cambiar config.js a localhost ─────────────────────────
Write-Host "  [3/4] Configurando frontend para modo local..." -ForegroundColor Yellow

$configContent = Get-Content $CONFIG_FILE -Raw
# Comentar la linea de produccion Railway y activar la de localhost
$configContent = $configContent -replace '(?m)^(// const WEBHOOK_URL = .+localhost.+)$', 'const WEBHOOK_URL = ''http://localhost:5678/webhook/chat-v2'';'
$configContent = $configContent -replace '(?m)^(const WEBHOOK_URL = .+railway\.app.+)$', '// $1'
$configContent | Set-Content $CONFIG_FILE -Encoding UTF8 -NoNewline
Write-Host "  [OK]  Webhook apuntando a localhost:5678" -ForegroundColor Green

# ── 4. Servidor frontend (puerto 3000) ───────────────────────
Write-Host "  [4/4] Iniciando servidor frontend..." -ForegroundColor Yellow

# Matar proceso anterior si habia uno en el puerto 3000
$oldPid = (Get-NetTCPConnection -LocalPort $FRONTEND_PORT -ErrorAction SilentlyContinue).OwningProcess | Select-Object -First 1
if ($oldPid) {
    Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Arrancar server.js como proceso independiente (ventana minimizada)
$serverFile = Join-Path $SCRIPT_DIR "server.js"
$serverProc = Start-Process -FilePath "node" -ArgumentList "`"$serverFile`"" `
    -WorkingDirectory $SCRIPT_DIR -WindowStyle Minimized -PassThru

# Esperar que el servidor responda (max 10s)
$serverReady = $false
for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Seconds 1
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:$FRONTEND_PORT" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $serverReady = $true; break }
    } catch {}
}

if ($serverReady) {
    Write-Host "  [OK]  Frontend en http://localhost:$FRONTEND_PORT" -ForegroundColor Green
} else {
    Write-Host "  [!]   Frontend puede tardar unos segundos mas." -ForegroundColor Yellow
}

# ── Estado final ─────────────────────────────────────────────
Write-Host ""
Write-Host "  Estado de servicios:" -ForegroundColor White
Write-Host ""

$svcs = @(
    @{ name = "sanos-n8n (Docker)"; check = { (docker inspect --format '{{.State.Status}}' $N8N_CONTAINER 2>$null) -eq "running" } },
    @{ name = "Agente n8n (webhook)"; check = { try { (Invoke-WebRequest "http://localhost:5678/healthz" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop).StatusCode -eq 200 } catch { $false } } },
    @{ name = "Frontend (localhost:3000)"; check = { try { (Invoke-WebRequest "http://localhost:$FRONTEND_PORT" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop).StatusCode -eq 200 } catch { $false } } }
)

foreach ($svc in $svcs) {
    $ok = & $svc.check
    if ($ok) {
        Write-Host "  [OK]  $($svc.name)" -ForegroundColor Green
    } else {
        Write-Host "  [--]  $($svc.name)" -ForegroundColor DarkGray
    }
}

# ── Abrir en el navegador ────────────────────────────────────
Start-Sleep -Seconds 1
Start-Process "http://localhost:$FRONTEND_PORT"
Start-Process "$N8N_URL/workflow/$WF_ID"

Write-Host ""
Write-Host "  ==========================================" -ForegroundColor Cyan
Write-Host "   SISTEMA LISTO - URLs de acceso:          " -ForegroundColor White
Write-Host "  ==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Frontend (sitio web)  ->  http://localhost:$FRONTEND_PORT" -ForegroundColor White
Write-Host "  n8n (agente AI)       ->  http://localhost:5678" -ForegroundColor White
Write-Host "  Webhook (chatbot)     ->  http://localhost:5678/webhook/chat-v2" -ForegroundColor White
Write-Host ""
Write-Host "  ==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  NOTA: Deja esta ventana abierta mientras usas el sistema." -ForegroundColor DarkGray
Write-Host "        El servidor frontend se detiene al cerrar esta ventana." -ForegroundColor DarkGray
Write-Host ""

Write-Host "  El servidor frontend corre en background." -ForegroundColor DarkGray
Write-Host "  Para detenerlo: cierra Docker o ejecuta 'Stop-Process -Name node'" -ForegroundColor DarkGray
