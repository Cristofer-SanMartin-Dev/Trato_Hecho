$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"

# 1. Llamar el webhook
Write-Host "Enviando mensaje..."
$body = '{"sessionId":"debug001","message":"hola"}'
try {
    $r = Invoke-WebRequest -Method POST -Uri "http://localhost:5678/webhook/chat" -Body $body -ContentType "application/json" -TimeoutSec 30
    Write-Host "Webhook Status: $($r.StatusCode)"
    Write-Host "Webhook Body: $($r.Content)"
} catch {
    Write-Host "Webhook error: $($_.Exception.Message)"
}

# 2. Esperar un poco
Start-Sleep -Milliseconds 2000

# 3. Ver la ultima ejecucion
$execs = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions?workflowId=CjS3Gm0863S4j9Ij&limit=1" -Headers @{"X-N8N-API-KEY"=$n8nKey}
$last = $execs.data[0]
Write-Host "`n=== Ultima ejecucion: ID $($last.id) Status: $($last.status) finished: $($last.finished) ==="
Write-Host "Duracion: $([datetime]$last.stoppedAt - [datetime]$last.startedAt)"

# 4. Ver datos de ejecucion
$detail = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions/$($last.id)" -Headers @{"X-N8N-API-KEY"=$n8nKey}
$detail | ConvertTo-Json -Depth 10 | Out-File "C:\Users\prueba\Downloads\last_exec.json" -Encoding UTF8
Write-Host "Guardado en last_exec.json"

# 5. Buscar error
$rawJson = Get-Content "C:\Users\prueba\Downloads\last_exec.json" -Raw
if ($rawJson -match '"message"\s*:\s*"([^"]+)"') {
    $rawJson | Select-String -Pattern '"message"\s*:\s*"[^"]+"' -AllMatches | ForEach-Object {
        $_.Matches | Select-Object -First 5 | ForEach-Object { Write-Host "MSG: $($_.Value)" }
    }
}
