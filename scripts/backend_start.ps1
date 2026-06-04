param(
  [string]$Config = "production",
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 5000
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path "$PSScriptRoot\.."
$backendRoot = Join-Path $repoRoot "backend"
$flask = Join-Path $repoRoot ".venv\Scripts\flask.exe"

Push-Location $backendRoot
try {
  $env:FLASK_CONFIG = $Config
  & $flask --app wsgi:app run --host $HostAddress --port $Port
}
finally {
  Pop-Location
}
