<#
.SYNOPSIS
    Tu dong cai dat moi truong dev (neu chua co) va khoi chay website tra cuu thu tuc hanh chinh cong VN.
.EXAMPLE
    .\run_develop.ps1
    .\run_develop.ps1 -LocalSqlite
    .\run_develop.ps1 -Port 8080
#>
param(
    [int]$Port = 8000,
    [Alias("sqlite", "sqllite", "local")]
    [switch]$LocalSqlite,
    [switch]$Reinstall
)

# Kiem tra ca tham so truyen vao tu do
foreach ($a in $args) {
    if ($a -match '(?i)^-?-?sql+ite$' -or $a -match '(?i)^-?-?local(sqlite)?$') {
        $LocalSqlite = $true
    }
    if ($a -match '(?i)^-?-?reinstall$') {
        $Reinstall = $true
    }
}

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Hanh chinh Cong VN - Khoi dong moi truong Develop (Windows)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Tim Python 3
$PythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    try {
        $ver = & py -3 --version 2>&1
        if ($LASTEXITCODE -eq 0) { $PythonCmd = @("py", "-3") }
    } catch {}
}
if (-not $PythonCmd -and (Get-Command python -ErrorAction SilentlyContinue)) {
    $ver = & python --version 2>&1
    if ($ver -match "Python 3\.") { $PythonCmd = @("python") }
}
if (-not $PythonCmd -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
    $PythonCmd = @("python3")
}

if (-not $PythonCmd) {
    Write-Host "[LOI] Khong tim thay Python 3. Vui long cai dat Python 3.11+ tai https://www.python.org/downloads/ (nho tick 'Add Python to PATH')." -ForegroundColor Red
    exit 1
}

Write-Host "[1/5] Su dung Python: $($PythonCmd -join ' ')" -ForegroundColor Green

# 2. Tao moi truong ao .venv neu chua co
$VenvDir = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[2/5] Dang tao moi truong ao .venv ..." -ForegroundColor Yellow
    if ($PythonCmd.Length -eq 2) {
        & $PythonCmd[0] $PythonCmd[1] -m venv $VenvDir
    } else {
        & $PythonCmd[0] -m venv $VenvDir
    }
} else {
    Write-Host "[2/5] Da co moi truong ao .venv." -ForegroundColor Green
}

# 3. Cai dat thu vien tu requirements.txt (chi chay lai khi requirements thay doi hoac -Reinstall)
$ReqFile = Join-Path $ProjectRoot "requirements.txt"
$HashFile = Join-Path $VenvDir ".requirements.sha256"
$CurrentHash = (Get-FileHash $ReqFile -Algorithm SHA256).Hash
$InstalledHash = if (Test-Path $HashFile) { (Get-Content $HashFile -Raw).Trim() } else { "" }

if ($Reinstall -or ($CurrentHash -ne $InstalledHash)) {
    Write-Host "[3/5] Dang cai dat cac thu vien Python trong requirements.txt ..." -ForegroundColor Yellow
    & $VenvPython -m pip install --upgrade pip --quiet
    & $VenvPython -m pip install -r $ReqFile
    Set-Content -Path $HashFile -Value $CurrentHash -NoNewline
} else {
    Write-Host "[3/5] Thu vien Python da day du." -ForegroundColor Green
}

# 4. Cau hinh .env va Database (uu tien PostgreSQL qua Docker, tu dong fallback SQLite neu chua bat Docker)
$EnvFile = Join-Path $ProjectRoot ".env"
$EnvExample = Join-Path $ProjectRoot ".env.example"
if (-not (Test-Path $EnvFile) -and (Test-Path $EnvExample)) {
    Copy-Item $EnvExample $EnvFile
}

# Doc bien tu .env neu nguoi dung chua set DATABASE_URL
if (-not $env:DATABASE_URL -and (Test-Path $EnvFile)) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+?)\s*=\s*(.+?)\s*$') {
            $k = $matches[1].Trim()
            $v = $matches[2].Trim().Trim('"').Trim("'")
            if (-not [Environment]::GetEnvironmentVariable($k, "Process")) {
                [Environment]::SetEnvironmentVariable($k, $v, "Process")
            }
        }
    }
}

if ($LocalSqlite) {
    $env:DATABASE_URL = "sqlite:///./dvc_local.db"
    Write-Host "[4/5] Che do nhanh (-LocalSqlite): Su dung SQLite cuc bo (dvc_local.db)." -ForegroundColor Yellow
} else {
    $DockerReady = $false
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        try {
            & docker info *> $null
            if ($LASTEXITCODE -eq 0) { $DockerReady = $true }
        } catch {}
    }

    if ($DockerReady) {
        Write-Host "[4/5] Dang khoi dong PostgreSQL 16 bang Docker Compose ..." -ForegroundColor Yellow
        & docker compose up -d postgres
        Write-Host "      Dang cho PostgreSQL san sang..." -ForegroundColor DarkGray
        for ($i = 0; $i -lt 20; $i++) {
            & docker compose exec -T postgres pg_isready -U dvc_user -d dvc_vietnam *> $null
            if ($LASTEXITCODE -eq 0) { break }
            Start-Sleep -Seconds 1
        }
        if (-not $env:DATABASE_URL) {
            $env:DATABASE_URL = "postgresql://dvc_user:dvc_secret_2026@localhost:5432/dvc_vietnam"
        }
        Write-Host "      PostgreSQL da san sang: $($env:DATABASE_URL)" -ForegroundColor Green
    } else {
        Write-Host "[4/5] Khong phat hien Docker dang chay -> Tu dong chuyen sang SQLite cuc bo (dvc_local.db)." -ForegroundColor Yellow
        Write-Host "      (Bat Docker Desktop va chay lai .\run_develop.ps1 de dung PostgreSQL 16)" -ForegroundColor DarkGray
        $env:DATABASE_URL = "sqlite:///./dvc_local.db"
    }
}

# 5. Dong bo file Markdown & khoi chay Uvicorn
Write-Host "[5/5] Dong bo thu muc procedures/*.md va khoi chay server..." -ForegroundColor Yellow
& $VenvPython scripts\sync_md.py

Write-Host ""
Write-Host "  Website dang chay tai : http://127.0.0.1:$Port" -ForegroundColor Green
Write-Host "  Trang cap nhat .md    : http://127.0.0.1:$Port/cap-nhat" -ForegroundColor Green
Write-Host "  Nhan Ctrl+C de dung server." -ForegroundColor DarkGray
Write-Host ""

& $VenvPython -m uvicorn app.main:app --reload --host 127.0.0.1 --port $Port
