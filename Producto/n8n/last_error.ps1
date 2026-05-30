$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"

$execs = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions?workflowId=CjS3Gm0863S4j9Ij&limit=1" -Headers @{"X-N8N-API-KEY"=$n8nKey}
$last = $execs.data[0]
Write-Host "Status: $($last.status)"
Write-Host "Finished: $($last.finished)"

$detail = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions/$($last.id)" -Headers @{"X-N8N-API-KEY"=$n8nKey}

# Buscar nodo con error
$detail.data.resultData.runData.PSObject.Properties | ForEach-Object {
    $nodeName = $_.Name
    $runs = $_.Value
    foreach ($run in $runs) {
        if ($run.error) {
            Write-Host "`n=== ERROR en nodo: $nodeName ==="
            Write-Host "Mensaje: $($run.error.message)"
            Write-Host "Stack: $($run.error.stack)"
        }
    }
}
