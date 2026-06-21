$n8nKey = $env:N8N_API_KEY
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# Nombres exactos de todos los nodos
Write-Host "=== NOMBRES DE NODOS ==="
$wf.nodes | ForEach-Object { Write-Host "[$($_.name)]" }

# Codigo del nodo Construir Prompt Claude (primeras 200 chars)
Write-Host "`n=== CODIGO Construir Prompt (inicio) ==="
$nodo = $wf.nodes | Where-Object { $_.name -like "*Construir*" }
$code = $nodo.parameters.jsCode
Write-Host $code.Substring(0, [Math]::Min(300, $code.Length))
