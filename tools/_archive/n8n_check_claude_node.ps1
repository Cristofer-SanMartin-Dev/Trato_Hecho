$n8nKey = $env:N8N_API_KEY

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
