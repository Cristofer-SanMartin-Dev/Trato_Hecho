$n8nKey = $env:N8N_API_KEY
$wf = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/CjS3Gm0863S4j9Ij" -Headers @{"X-N8N-API-KEY"=$n8nKey}
$wf.nodes | Select-Object name | Sort-Object name | Format-Table -AutoSize
