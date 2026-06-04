param(
  [Parameter(Mandatory = $true)][string]$Database,
  [Parameter(Mandatory = $true)][string]$User,
  [Parameter(Mandatory = $true)][string]$OutputPath,
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 3306
)

$ErrorActionPreference = "Stop"
$outputDir = Split-Path -Parent $OutputPath
if ($outputDir -and -not (Test-Path $outputDir)) {
  New-Item -ItemType Directory -Path $outputDir | Out-Null
}

mysqldump --host=$HostAddress --port=$Port --user=$User --single-transaction --routines --triggers $Database | Out-File -FilePath $OutputPath -Encoding utf8
