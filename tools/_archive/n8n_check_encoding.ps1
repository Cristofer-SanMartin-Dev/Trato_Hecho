$n8nKey = $env:N8N_API_KEY

# 1. Leer workflow actual
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# 2. Obtener nombre exacto del nodo Redis de cotizacion (con su encoding real)
$redisNode = $wf.nodes | Where-Object { $_.name -like "*otizaci*" -and $_.name -like "*Redis*" }
Write-Host "Nombre exacto del nodo Redis cotizacion: [$($redisNode.name)]"

# Mostrar bytes del nombre
$bytes = [System.Text.Encoding]::UTF8.GetBytes($redisNode.name)
Write-Host "Bytes UTF8: $($bytes -join ' ')"
