param(
    [int]$Port = 9000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot
try {
    if (-not (Test-Path .venv)) {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            py -3 -m venv .venv
        } else {
            python -m venv .venv
        }
    }

    .\.venv\Scripts\python -m ensurepip --upgrade
    .\.venv\Scripts\python -m pip install --upgrade pip
    .\.venv\Scripts\python -m pip install fastapi "uvicorn[standard]" SQLAlchemy pandas | Out-Host

    Write-Host "Verifying installs..." -ForegroundColor Yellow
    .\.venv\Scripts\python -c "import sqlalchemy, pandas; print('sqlalchemy', sqlalchemy.__version__, '| pandas', pandas.__version__)" | Out-Host

    Write-Host "Starting API on http://127.0.0.1:$Port ..." -ForegroundColor Cyan
    .\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port $Port
}
finally {
    Pop-Location
}
