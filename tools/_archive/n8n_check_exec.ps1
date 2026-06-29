$n8nKey = $env:N8N_API_KEY
$headers = @{ "X-N8N-API-KEY" = $n8nKey }
$execs = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions?workflowId=CjS3Gm0863S4j9Ij&limit=1&includeData=true" -Headers $headers
$last = $execs.data[0]
Write-Host "=== Estado: $($last.status) ==="
$last.data.resultData.error | ConvertTo-Json -Depth 3
