$n8nKey = $env:N8N_API_KEY
$headers = @{ "X-N8N-API-KEY" = $n8nKey }

# Obtener flujo
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers $headers

# Asignar credencial al nodo Claude
foreach ($node in $wf.nodes) {
    if ($node.name -eq "API de Llamar Claude") {
        $node.credentials = [PSCustomObject]@{
            httpHeaderAuth = [PSCustomObject]@{
                id   = "GoQq4Na0MeD7nLo1"
                name = "Claude - Trato Hecho"
            }
        }
        Write-Host "Credencial asignada al nodo: $($node.name)"
    }
}

# Construir body solo con campos permitidos por la API
$putBody = @{
    name        = $wf.name
    nodes       = $wf.nodes
    connections = $wf.connections
    settings    = @{}
    staticData  = $null
} | ConvertTo-Json -Depth 20 -Compress

$r = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Method PUT -ContentType "application/json" -Headers $headers -Body $putBody
Write-Host "Flujo actualizado: $($r.name)"
