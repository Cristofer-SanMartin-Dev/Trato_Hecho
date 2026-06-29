$n8nKey = $env:N8N_API_KEY

# Disparar un webhook nuevo y esperar mas tiempo
Write-Host "Disparando webhook..."
$body = @{ uuid = "test-$(Get-Date -Format 'HHmmss')"; message = "hola" } | ConvertTo-Json
$resp = Invoke-WebRequest -Uri "http://localhost:5678/webhook/chat" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
Write-Host "Status: $($resp.StatusCode)"
Write-Host "Body: $($resp.Content)"
Start-Sleep -Milliseconds 3000

# Buscar la ultima ejecucion
$execs = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions?limit=1" -Headers @{"X-N8N-API-KEY"=$n8nKey}
$lastId = $execs.data[0].id
Write-Host "=== Execution ID: $lastId ==="

$exec = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions/$lastId" -Headers @{"X-N8N-API-KEY"=$n8nKey}
$exec | ConvertTo-Json -Depth 20 | Out-File "C:\Users\prueba\Downloads\exec_detail.json" -Encoding UTF8

# Mostrar info clave
Write-Host "Status: $($exec.status)"
Write-Host "Finished: $($exec.finished)"
Write-Host ""
Write-Host "=== resultData nodes que corrieron ==="
$runData = $exec.data.resultData.runData
if ($runData) {
    $runData.PSObject.Properties | ForEach-Object {
        Write-Host "Nodo: '$($_.Name)' - ejecutado"
    }
} else {
    Write-Host "VACIO - runData es null"
}

Write-Host ""
Write-Host "=== Error principal ==="
$err = $exec.data.resultData.error
Write-Host "Error: $($err | ConvertTo-Json -Depth 5)"
