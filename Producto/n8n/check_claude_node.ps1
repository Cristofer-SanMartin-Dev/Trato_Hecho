$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"

$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}
$claude = $wf.nodes | Where-Object { $_.name -eq "Llamar Claude API" }

Write-Host "=== Llamar Claude API - parametros ==="
Write-Host "authentication: $($claude.parameters.authentication)"
Write-Host "genericAuthType: $($claude.parameters.genericAuthType)"
Write-Host "specifyBody: $($claude.parameters.specifyBody)"
Write-Host "body: $($claude.parameters.body)"
Write-Host "jsonBody: $($claude.parameters.jsonBody)"
Write-Host "`n=== Credenciales ==="
$claude.credentials | ConvertTo-Json -Depth 3

# Tambien check Construir Prompt - primeras 2 lineas
Write-Host "`n=== Construir Prompt (primeras 2 lineas) ==="
$cp = $wf.nodes | Where-Object { $_.name -eq "Construir Prompt Claude" }
($cp.parameters.jsCode -split "`n")[0..2] | ForEach-Object { Write-Host $_ }
