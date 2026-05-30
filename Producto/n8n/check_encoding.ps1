$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"

# 1. Leer workflow actual
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# 2. Obtener nombre exacto del nodo Redis de cotizacion (con su encoding real)
$redisNode = $wf.nodes | Where-Object { $_.name -like "*otizaci*" -and $_.name -like "*Redis*" }
Write-Host "Nombre exacto del nodo Redis cotizacion: [$($redisNode.name)]"

# Mostrar bytes del nombre
$bytes = [System.Text.Encoding]::UTF8.GetBytes($redisNode.name)
Write-Host "Bytes UTF8: $($bytes -join ' ')"
