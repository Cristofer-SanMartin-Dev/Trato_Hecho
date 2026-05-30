$apiKey = $env:ANTHROPIC_API_KEY  # Set via environment variable

$body = '{"model":"claude-sonnet-4-5","max_tokens":10,"messages":[{"role":"user","content":"hola"}]}'

try {
    $r = Invoke-WebRequest -Method POST `
        -Uri "https://api.anthropic.com/v1/messages" `
        -Headers @{
            "x-api-key" = $apiKey
            "anthropic-version" = "2023-06-01"
            "content-type" = "application/json"
        } `
        -Body $body `
        -TimeoutSec 15
    Write-Host "Status: $($r.StatusCode)"
    Write-Host "Body: $($r.Content)"
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        Write-Host "Response: $($reader.ReadToEnd())"
    }
}
