# ============================================================
#  Prende la instancia EC2 y espera a que n8n + frontend
#  respondan. Docker (n8n) y el frontend (systemd) arrancan
#  solos al bootear -- no hace falta reinstalar nada.
#
#  Requisito previo: haber corrido aws-refresh-creds.ps1 con
#  las credenciales frescas de tu Learner Lab de hoy.
# ============================================================

$ErrorActionPreference = "Stop"
Push-Location "$PSScriptRoot"

Write-Host "Verificando credenciales de AWS..." -ForegroundColor Cyan
try {
    aws sts get-caller-identity --profile academy | Out-Null
} catch {
    Write-Host "[ERROR] Credenciales invalidas o vencidas. Corre primero: .\aws-refresh-creds.ps1" -ForegroundColor Red
    Pop-Location
    exit 1
}

$instanceId = terraform output -raw instance_id
$publicIp   = terraform output -raw public_ip

$state = aws ec2 describe-instances --instance-ids $instanceId --profile academy --query "Reservations[0].Instances[0].State.Name" --output text
if ($state -eq "running") {
    Write-Host "La instancia ya esta corriendo." -ForegroundColor Green
} else {
    Write-Host "Prendiendo instancia $instanceId ..." -ForegroundColor Yellow
    aws ec2 start-instances --instance-ids $instanceId --profile academy | Out-Null
    aws ec2 wait instance-running --instance-ids $instanceId --profile academy
    Write-Host "Instancia arriba. Esperando que los servicios respondan (Docker/n8n tardan ~15-30s en arrancar)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20
}

# Reintentos porque n8n puede tardar unos segundos extra en levantar tras el boot
$maxTries = 10
$ready = $false
for ($i = 0; $i -lt $maxTries; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://$publicIp`:5678/healthz" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 5
}

Write-Host ""
if ($ready) {
    Write-Host "n8n respondiendo correctamente." -ForegroundColor Green
} else {
    Write-Host "n8n todavia no responde despues de esperar. Puede necesitar mas tiempo, o revisar por SSH." -ForegroundColor Yellow
}

$niphost = "$publicIp.nip.io"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Frontend:  http://$publicIp`:3000"
Write-Host " n8n:       http://$publicIp`:5678"
Write-Host " Webhook:   http://$publicIp`:5678/webhook/chat-v2"
Write-Host "------------------------------------------" -ForegroundColor DarkGray
Write-Host " Para Gmail/OAuth usa SIEMPRE este host (es" -ForegroundColor DarkGray
Write-Host " el que quedo registrado en Google Cloud):" -ForegroundColor DarkGray
Write-Host " n8n (OAuth): http://$niphost`:5678" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

Pop-Location
