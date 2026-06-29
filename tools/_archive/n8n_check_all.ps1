$n8nKey = $env:N8N_API_KEY

# Ver todos los flujos
$all = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows?limit=50" -Headers @{"X-N8N-API-KEY"=$n8nKey}
Write-Host "=== TODOS LOS FLUJOS ==="
$all.data | ForEach-Object {
    Write-Host "[$($_.id)] '$($_.name)' - active: $($_.active)"
}

# Ver ultimas 5 ejecuciones con estado
Write-Host "`n=== ULTIMAS 5 EJECUCIONES ==="
$execs = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions?limit=5" -Headers @{"X-N8N-API-KEY"=$n8nKey}
$execs.data | ForEach-Object {
    Write-Host "ID: $($_.id)  wf: $($_.workflowId)  status: $($_.status)  finished: $($_.finished)  dur: $(([datetime]$_.stoppedAt - [datetime]$_.startedAt).TotalMilliseconds)ms"
}
