$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"

$detail = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions/111" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# Dump completo como JSON para ver toda la estructura
$detail | ConvertTo-Json -Depth 8 | Out-File "C:\Users\prueba\Downloads\exec111.json" -Encoding UTF8
Write-Host "Guardado en exec111.json"

# Intentar ver el error directamente
Write-Host "`n=== data.resultData keys ==="
$detail.data.resultData | Get-Member -MemberType NoteProperty | Select-Object Name

Write-Host "`n=== lastNodeExecuted ==="
Write-Host $detail.data.resultData.lastNodeExecuted
