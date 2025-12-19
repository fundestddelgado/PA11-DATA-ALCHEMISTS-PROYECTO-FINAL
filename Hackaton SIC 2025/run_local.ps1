$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$BackendPort = 8000
$FrontendPort = 8001

Write-Host "[init] Backend: $BackendPort | Frontend: $FrontendPort"
Write-Host "[info] Asegúrate de instalar dependencias: pip install -r backend/requirements.txt"

# Selecciona intérprete Python (prefiere el de .venv si existe)
$VenvPython = Join-Path $Backend ".venv/Scripts/python.exe"
if (Test-Path $VenvPython) {
  $Python = $VenvPython
} else {
  $Python = "python"
}

# Inicia frontend en segundo plano
Write-Host "[start] Frontend sirviendo en http://localhost:$FrontendPort"
$FrontendJob = Start-Process -FilePath $Python `
  -ArgumentList "-m", "http.server", "$FrontendPort" `
  -WorkingDirectory $Frontend `
  -PassThru -NoNewWindow

try {
  # Inicia backend en primer plano (Ctrl+C para salir)
  Write-Host "[start] Backend en http://localhost:$BackendPort (Ctrl+C para detener)"
  & $Python -m uvicorn main:app --host 0.0.0.0 --port $BackendPort --reload
} finally {
  if ($FrontendJob -and !$FrontendJob.HasExited) {
    Write-Host "[stop] Cerrando frontend"
    $FrontendJob.Kill()
  }
}
