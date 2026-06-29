$n8nKey = $env:N8N_API_KEY

# 1. Leer workflow actual
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# 2. Obtener nodo Construir Prompt Claude
$nodo = $wf.nodes | Where-Object { $_.name -eq "Construir Prompt Claude" }

# 3. Reemplazar la referencia problematica por $input
$oldRef = '$(' + "'Obtener Cotizaci" + [char]0x00F3 + "n Redis'" + ').first().json'
$newRef = '$input.first().json'
$nodo.parameters.jsCode = $nodo.parameters.jsCode.Replace($oldRef, $newRef)

# Verificar que se hizo el reemplazo
if ($nodo.parameters.jsCode -match '\$input\.first\(\)\.json') {
    Write-Host "Reemplazo OK - usando `$input"
} else {
    Write-Host "FALLO el reemplazo, intentando con replacement char..."
    $oldRef2 = '$(' + "'Obtener Cotizaci" + [char]0xFFFD + "n Redis'" + ').first().json'
    $nodo.parameters.jsCode = $nodo.parameters.jsCode.Replace($oldRef2, $newRef)
    Write-Host "Segundo intento: $($nodo.parameters.jsCode -match '\$input\.first\(\)\.json')"
}

# 4. Preparar payload solo con nodes y connections
$payload = @{
    name        = $wf.name
    nodes       = $wf.nodes
    connections = $wf.connections
    settings    = @{ executionOrder = "v1" }
} | ConvertTo-Json -Depth 100

# 5. Enviar
$result = Invoke-RestMethod -Method PUT `
    -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" `
    -Headers @{"X-N8N-API-KEY"=$n8nKey; "Content-Type"="application/json"} `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($payload))

Write-Host "Deploy OK: $($result.name)"
