$n8nKey = $env:N8N_API_KEY

$detail = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions/111" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# Dump completo como JSON para ver toda la estructura
$detail | ConvertTo-Json -Depth 8 | Out-File "C:\Users\prueba\Downloads\exec111.json" -Encoding UTF8
Write-Host "Guardado en exec111.json"

# Intentar ver el error directamente
Write-Host "`n=== data.resultData keys ==="
$detail.data.resultData | Get-Member -MemberType NoteProperty | Select-Object Name

Write-Host "`n=== lastNodeExecuted ==="
Write-Host $detail.data.resultData.lastNodeExecuted
