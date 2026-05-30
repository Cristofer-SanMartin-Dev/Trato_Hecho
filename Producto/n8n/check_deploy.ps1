$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# Nombres exactos de todos los nodos
Write-Host "=== NOMBRES DE NODOS ==="
$wf.nodes | ForEach-Object { Write-Host "[$($_.name)]" }

# Codigo del nodo Construir Prompt Claude (primeras 200 chars)
Write-Host "`n=== CODIGO Construir Prompt (inicio) ==="
$nodo = $wf.nodes | Where-Object { $_.name -like "*Construir*" }
$code = $nodo.parameters.jsCode
Write-Host $code.Substring(0, [Math]::Min(300, $code.Length))
