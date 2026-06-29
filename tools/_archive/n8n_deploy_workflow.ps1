$n8nKey = $env:N8N_API_KEY
$json = Get-Content "C:\Users\prueba\Downloads\Trato Hecho - Chat Agent (2).json" -Raw -Encoding UTF8
$body = $json | ConvertFrom-Json

$payload = @{
  name = $body.name
  nodes = $body.nodes
  connections = $body.connections
  settings = @{
    executionOrder = "v1"
  }
} | ConvertTo-Json -Depth 100

$result = Invoke-RestMethod -Method PUT `
  -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" `
  -Headers @{"X-N8N-API-KEY"=$n8nKey; "Content-Type"="application/json"} `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($payload))

Write-Host "OK: $($result.name) - active: $($result.active)"
