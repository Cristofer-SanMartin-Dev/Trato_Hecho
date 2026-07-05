# ============================================================
#  Apaga la instancia EC2 (no la destruye, no borra nada).
#  Ahorra horas de tu presupuesto de AWS Academy mientras no
#  estás usando el sistema.
# ============================================================

$ErrorActionPreference = "Stop"
Push-Location "$PSScriptRoot"

$instanceId = terraform output -raw instance_id
Write-Host "Apagando instancia $instanceId ..." -ForegroundColor Yellow

aws ec2 stop-instances --instance-ids $instanceId --profile academy | Out-Null
aws ec2 wait instance-stopped --instance-ids $instanceId --profile academy

Write-Host "Instancia detenida." -ForegroundColor Green
Write-Host "La IP publica ($((terraform output -raw public_ip))) queda reservada (Elastic IP) -- no cambia al volver a prenderla." -ForegroundColor DarkGray

Pop-Location
