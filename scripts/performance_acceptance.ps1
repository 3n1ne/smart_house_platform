param(
    [string]$BaseUrl = "http://127.0.0.1:5000",
    [int]$Requests = 1000,
    [int]$Concurrency = 1000,
    [double]$TargetSeconds = 2,
    [string[]]$Endpoints = @("/api/houses", "/api/search/regions", "/api/search/layouts")
)

$ErrorActionPreference = "Stop"
$python = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } else { "python" }

foreach ($endpoint in $Endpoints) {
    $url = $BaseUrl.TrimEnd("/") + $endpoint
    Write-Host "Testing $url with $Requests requests / $Concurrency concurrency"
    & $python backend\scripts\performance_smoke.py `
        --url $url `
        --requests $Requests `
        --concurrency $Concurrency `
        --target-seconds $TargetSeconds
}
