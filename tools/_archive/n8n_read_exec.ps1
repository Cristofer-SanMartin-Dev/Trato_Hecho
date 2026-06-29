$file = Get-Content "C:\Users\prueba\Downloads\exec111.json" -Raw
# Buscar lineas con error o message
$lines = $file -split "`n"
$lines | Where-Object { $_ -match '"message"|"error"|"lastNode"|"stack"' } | Select-Object -First 20
