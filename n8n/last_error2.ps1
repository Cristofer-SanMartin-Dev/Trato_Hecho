$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"

$execs = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions?workflowId=CjS3Gm0863S4j9Ij&limit=3" -Headers @{"X-N8N-API-KEY"=$n8nKey}

foreach ($exec in $execs.data) {
    Write-Host "--- Exec ID: $($exec.id) Status: $($exec.status) ---"
    
    $detail = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions/$($exec.id)" -Headers @{"X-N8N-API-KEY"=$n8nKey}
    
    # Dump completo del error de ejecucion
    if ($detail.data.resultData.error) {
        Write-Host "ERROR GLOBAL: $($detail.data.resultData.error | ConvertTo-Json -Depth 3)"
    }
    
    # Ver cada nodo
    $detail.data.resultData.runData.PSObject.Properties | ForEach-Object {
        $nodeName = $_.Name
        $runs = $_.Value
        foreach ($run in $runs) {
            if ($run.error) {
                Write-Host "`nNODO: $nodeName"
                Write-Host "ERROR: $($run.error | ConvertTo-Json -Depth 2)"
            }
        }
    }
    break  # solo el primero
}
