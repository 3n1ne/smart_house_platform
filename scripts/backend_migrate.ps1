param(
  [string]$Config = "production"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path "$PSScriptRoot\.."
$backendRoot = Join-Path $repoRoot "backend"
$flask = Join-Path $repoRoot ".venv\Scripts\flask.exe"

Push-Location $backendRoot
try {
  $env:FLASK_CONFIG = $Config
  & $flask --app run:app db upgrade
}
finally {
  Pop-Location
}
