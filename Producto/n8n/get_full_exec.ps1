$n8nKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNDg1MWM1ZS1hODlhLTQ5ODQtYWY2MS0yMTNiYTg4NGFhZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDRmMzU4MzEtN2Q4ZS00YzhiLThmZDctZDhkYWJmYzNkYmY0IiwiaWF0IjoxNzc3Njg5NTgyLCJleHAiOjE3ODAyMDAwMDB9.q7ZZHqgXYNZr_N6tBpIqkJ3sNAfsTe2xfoXMKek9Gcw"

# Intentar API v1 con includeData
Write-Host "=== Intento 1: includeData=true ==="
try {
    $r = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions/115?includeData=true" -Headers @{"X-N8N-API-KEY"=$n8nKey}
    $r | ConvertTo-Json -Depth 20 | Out-File "C:\Users\prueba\Downloads\exec_withdata.json" -Encoding UTF8
    Write-Host "data field exists: $($null -ne $r.data)"
    Write-Host "Keys: $($r.PSObject.Properties.Name -join ', ')"
    if ($r.data) {
        Write-Host "data keys: $($r.data.PSObject.Properties.Name -join ', ')"
        if ($r.data.resultData) {
            Write-Host "resultData: $($r.data.resultData | ConvertTo-Json -Depth 5)"
        }
        if ($r.data.executionData) {
            Write-Host "executionData: $($r.data.executionData | ConvertTo-Json -Depth 3)"
        }
    }
} catch {
    Write-Host "Error: $_"
}

# Intentar internal API
Write-Host "`n=== Intento 2: internal REST API /rest/executions ==="
try {
    $r2 = Invoke-RestMethod -Uri "http://localhost:5678/rest/executions/115" -Headers @{"X-N8N-API-KEY"=$n8nKey}
    Write-Host "Keys: $($r2.PSObject.Properties.Name -join ', ')"
    if ($r2.data) {
        Write-Host "data.executionData: $($r2.data.executionData | ConvertTo-Json -Depth 3)"
        Write-Host "data.resultData.error: $($r2.data.resultData.error | ConvertTo-Json -Depth 3)"
        Write-Host "data.resultData.lastNodeExecuted: $($r2.data.resultData.lastNodeExecuted)"
    }
} catch {
    Write-Host "Error internal: $_"
}
