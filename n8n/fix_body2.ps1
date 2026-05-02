$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"

# Leer workflow actual
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# Parchear Llamar Claude API
$nodes = $wf.nodes
for ($i = 0; $i -lt $nodes.Count; $i++) {
    if ($nodes[$i].name -eq "Llamar Claude API") {
        $nodes[$i].parameters.specifyBody = "json"
        $nodes[$i].parameters | Add-Member -NotePropertyName "jsonBody" -NotePropertyValue '={{ JSON.parse($json.claudeBody) }}' -Force
        $nodes[$i].parameters.PSObject.Properties.Remove("body")
        Write-Host "Nodo parcheado OK"
    }
}

# Settings solo con campos permitidos por la API
$settings = @{
    executionOrder = $wf.settings.executionOrder
    callerPolicy   = $wf.settings.callerPolicy
}
if ($wf.settings.timezone) { $settings.timezone = $wf.settings.timezone }

$payload = @{
    name        = $wf.name
    nodes       = $wf.nodes
    connections = $wf.connections
    settings    = $settings
    staticData  = if ($wf.staticData) { $wf.staticData } else { @{} }
} | ConvertTo-Json -Depth 30

# Deploy
$headers = @{"X-N8N-API-KEY"=$n8nKey; "Content-Type"="application/json"}
$result = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Method PUT -Headers $headers -Body $payload
Write-Host "Deploy OK: $($result.name)"

# Reactivar
$null = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij/activate" -Method POST -Headers $headers -ContentType "application/json" -Body "{}"
Write-Host "Reactivado"

# Test
Start-Sleep -Seconds 1
$testBody = '{"uuid":"fix002","message":"hola"}'
$r = Invoke-WebRequest -Uri "http://localhost:5678/webhook/chat" -Method POST -ContentType "application/json" -Body $testBody -TimeoutSec 35
Write-Host "STATUS: $($r.StatusCode)"
Write-Host "RESPUESTA: $($r.Content)"
