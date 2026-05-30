$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"

# 1. Leer workflow actual
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# 2. Encontrar el nodo y ver el codigo actual exacto
$nodo = $wf.nodes | Where-Object { $_.name -eq "Construir Prompt Claude" }
$code = $nodo.parameters.jsCode

# 3. Mostrar las primeras 3 lineas con bytes para ver encoding real
Write-Host "=== Primeras 3 lineas del codigo actual ==="
$lines = $code -split "`n"
$lines[0..3] | ForEach-Object { 
    Write-Host $_
    $b = [System.Text.Encoding]::UTF8.GetBytes($_)
    Write-Host "   Bytes: $($b[0..([Math]::Min(30, $b.Length-1))] -join ' ')"
}

# 4. Buscar exactamente cual es el problema - listar todas las referencias $('...')
Write-Host "`n=== Referencias a nodos en el codigo ==="
$refs = [regex]::Matches($code, "\`$\('([^']+)'\)")
foreach ($ref in $refs) {
    $name = $ref.Groups[1].Value
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($name)
    Write-Host "Ref: [$name]  Bytes: $($bytes -join ' ')"
}
