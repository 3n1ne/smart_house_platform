param(
    [switch]$SkipBackendTests,
    [switch]$SkipNpmAudit
)

$ErrorActionPreference = "Stop"
$python = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } else { "python" }

Write-Host "Checking Python syntax for security-sensitive modules"
& $python -m py_compile `
    backend\app\api\auth.py `
    backend\app\api\user.py `
    backend\app\utils\auth.py `
    backend\app\utils\sensitive.py

if (-not $SkipBackendTests) {
    Write-Host "Running security regression tests"
    & $python -m pytest `
        backend\tests\test_auth_mfa_api.py `
        backend\tests\test_permission_boundaries_api.py `
        backend\tests\test_sensitive_profile_api.py `
        --basetemp .pytest_tmp_security
}

if (-not $SkipNpmAudit) {
    Write-Host "Running frontend npm audit"
    Push-Location frontend
    try {
        npm audit --omit=dev --audit-level=high
    }
    finally {
        Pop-Location
    }
}

Write-Host "Manual production checks still required: HTTPS certificate, firewall rules, IDS/WAF policy, server vulnerability scan report."
