param(
    [string]$BaseUrl = "http://127.0.0.1:5173",
    [string[]]$Paths = @("/", "/login", "/register", "/houses", "/news")
)

$ErrorActionPreference = "Stop"

foreach ($path in $Paths) {
    $url = $BaseUrl.TrimEnd("/") + $path
    Write-Host "Checking $url"
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 400) {
        throw "Unexpected HTTP status $($response.StatusCode) for $url"
    }
}

Write-Host "HTTP page smoke check passed. Record real Chrome/Firefox/Edge/360/mobile browser results in docs/compatibility-checklist.md."
