$n8nKey = $env:N8N_API_KEY

# Leer workflow actual
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# Encontrar y parchear el nodo Llamar Claude API
$nodes = $wf.nodes
for ($i = 0; $i -lt $nodes.Count; $i++) {
    if ($nodes[$i].name -eq "Llamar Claude API") {
        Write-Host "Antes: specifyBody=$($nodes[$i].parameters.specifyBody) body=$($nodes[$i].parameters.body)"
        
        # Cambiar a specifyBody: json y jsonBody con JSON.parse
        $nodes[$i].parameters.specifyBody = "json"
        $nodes[$i].parameters | Add-Member -NotePropertyName "jsonBody" -NotePropertyValue '={{ JSON.parse($json.claudeBody) }}' -Force
        # Quitar el campo body incorrecto
        $nodes[$i].parameters.PSObject.Properties.Remove("body")
        
        Write-Host "Despues: specifyBody=$($nodes[$i].parameters.specifyBody) jsonBody=$($nodes[$i].parameters.jsonBody)"
    }
}

# Preparar payload para PUT
$payload = @{
    name        = $wf.name
    nodes       = $wf.nodes
    connections = $wf.connections
    settings    = $wf.settings
    staticData  = $wf.staticData
} | ConvertTo-Json -Depth 30

# Deploy
$result = Invoke-RestMethod `
    -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" `
    -Method PUT `
    -Headers @{"X-N8N-API-KEY"=$n8nKey; "Content-Type"="application/json"} `
    -Body $payload

Write-Host "Deploy OK: $($result.name)"

# Reactivar
Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij/activate" -Method POST -Headers @{"X-N8N-API-KEY"=$n8nKey} | Out-Null
Write-Host "Reactivado"

# Test rapido
Start-Sleep -Seconds 1
$body = '{"uuid":"fix001","message":"hola"}'
$r = Invoke-WebRequest -Uri "http://localhost:5678/webhook/chat" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
Write-Host "Status: $($r.StatusCode)"
Write-Host "Body: $($r.Content)"
