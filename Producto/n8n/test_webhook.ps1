$body = '{"sessionId":"test123","message":"hola"}'
try {
    $r = Invoke-WebRequest -Method POST -Uri "http://localhost:5678/webhook/chat" -Body $body -ContentType "application/json" -TimeoutSec 15
    Write-Host "Status: $($r.StatusCode)"
    Write-Host "Body: $($r.Content)"
} catch {
    Write-Host "Error HTTP: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        Write-Host "Response body: $($reader.ReadToEnd())"
    }
}
