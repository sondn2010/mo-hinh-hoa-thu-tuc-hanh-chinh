@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ============================================================
:: Hanh chinh Cong VN - Script khoi chay moi truong Develop (Windows)
:: Ho tro chay truc tiep tu thu muc goc hoac thu muc src\
:: ============================================================

:: 0. Xac dinh thu muc du an (chua requirements.txt va app\)
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%requirements.txt" (
    set "PROJECT_ROOT=%SCRIPT_DIR%"
) else if exist "%SCRIPT_DIR%src\requirements.txt" (
    set "PROJECT_ROOT=%SCRIPT_DIR%src\"
) else (
    set "PROJECT_ROOT=%SCRIPT_DIR%"
)
cd /d "%PROJECT_ROOT%"

:: 1. Tham so mac dinh
set "PORT=8000"
set "LOCAL_SQLITE=0"
set "REINSTALL=0"

:parse_args
if "%~1"=="" goto after_args

set "ARG=%~1"

:: Kiem tra cac bien the cua sqlite / sqllite / local
if /i "!ARG!"=="--sqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="-sqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="/sqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="sqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="--sqllite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="-sqllite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="/sqllite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="sqllite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="--localsqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="-localsqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="/localsqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="localsqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="-LocalSqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="--LocalSqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="LocalSqlite" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="--local" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="-local" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="/local" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )
if /i "!ARG!"=="local" ( set "LOCAL_SQLITE=1" & shift & goto parse_args )

:: Kiem tra cac bien the cua reinstall
if /i "!ARG!"=="--reinstall" ( set "REINSTALL=1" & shift & goto parse_args )
if /i "!ARG!"=="-reinstall" ( set "REINSTALL=1" & shift & goto parse_args )
if /i "!ARG!"=="/reinstall" ( set "REINSTALL=1" & shift & goto parse_args )
if /i "!ARG!"=="reinstall" ( set "REINSTALL=1" & shift & goto parse_args )

:: Kiem tra port
if /i "!ARG!"=="--port" ( set "PORT=%~2" & shift & shift & goto parse_args )
if /i "!ARG!"=="-port" ( set "PORT=%~2" & shift & shift & goto parse_args )
if /i "!ARG!"=="/port" ( set "PORT=%~2" & shift & shift & goto parse_args )
if /i "!ARG!"=="port" ( set "PORT=%~2" & shift & shift & goto parse_args )

if /i "!ARG!"=="-h" goto show_help
if /i "!ARG!"=="--help" goto show_help
if /i "!ARG!"=="/?" goto show_help

echo [CANH BAO] Tham so khong ho tro: %~1
shift
goto parse_args

:show_help
echo ============================================================
echo   Hanh chinh Cong VN - Cach dung run_develop.bat
echo ============================================================
echo   run_develop.bat              : Chay mac dinh [PostgreSQL neu co Docker, fallback SQLite]
echo   run_develop.bat --sqlite     : Chay nhanh bang SQLite cuc bo [dvc_local.db]
echo   run_develop.bat sqllite      : Chay nhanh bang SQLite cuc bo [dvc_local.db]
echo   run_develop.bat --port 8080  : Doi cong lang nghe sang 8080
echo   run_develop.bat --reinstall : Ep buoc cai dat lai cac thu vien Python
echo.
exit /b 0

:after_args

echo ============================================================
echo   Hanh chinh Cong VN - Khoi dong moi truong Develop (Windows)
echo ============================================================

:: 2. Tim Python 3
set "PYTHON_CMD="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"

if "%PYTHON_CMD%"=="" (
    python --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if "%PYTHON_CMD%"=="" (
    python3 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python3"
)

if "%PYTHON_CMD%"=="" (
    echo [LOI] Khong tim thay Python 3 tren he thong.
    echo Vui long cai dat Python 3.10+ tai https://www.python.org/downloads/
    echo Luu y: Nho danh dau vao o "Add Python to PATH" khi cai dat.
    pause
    exit /b 1
)

for /f "delims=" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set "PY_VER=%%v"
echo [1/5] Su dung Python: %PYTHON_CMD% [%PY_VER%]

:: 3. Tao moi truong ao .venv neu chua co
set "VENV_DIR=%PROJECT_ROOT%.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    echo [2/5] Da co moi truong ao .venv.
) else (
    echo [2/5] Dang tao moi truong ao .venv ...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [LOI] Khong the tao moi truong ao .venv!
        pause
        exit /b 1
    )
    echo       Moi truong ao .venv da duoc tao thanh cong.
)

:: 4. Cai dat dependencies tu requirements.txt
set "REQ_FILE=%PROJECT_ROOT%requirements.txt"
set "HASH_FILE=%VENV_DIR%\.requirements.sha256"
set "NEED_INSTALL=0"

if not exist "%REQ_FILE%" (
    echo [LOI] Khong tim thay file requirements.txt tai %REQ_FILE%!
    pause
    exit /b 1
)

if "%REINSTALL%"=="1" set "NEED_INSTALL=1"
if not exist "%HASH_FILE%" set "NEED_INSTALL=1"

if "!NEED_INSTALL!"=="0" (
    "%VENV_PYTHON%" -c "import hashlib, pathlib, sys; h1 = hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest(); h2 = pathlib.Path(sys.argv[2]).read_text().strip(); sys.exit(0 if h1 == h2 else 1)" "%REQ_FILE%" "%HASH_FILE%" >nul 2>&1
    if errorlevel 1 set "NEED_INSTALL=1"
)

if "!NEED_INSTALL!"=="1" (
    echo [3/5] Dang cai dat cac thu vien Python tu requirements.txt ...
    "%VENV_PYTHON%" -m pip install --upgrade pip --quiet
    "%VENV_PYTHON%" -m pip install -r "%REQ_FILE%"
    if errorlevel 1 (
        echo [LOI] Cai dat dependencies that bai!
        pause
        exit /b 1
    )
    "%VENV_PYTHON%" -c "import hashlib, pathlib, sys; pathlib.Path(sys.argv[2]).write_text(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())" "%REQ_FILE%" "%HASH_FILE%" >nul 2>&1
    echo       Cai dat dependencies hoan tat.
) else (
    echo [3/5] Thu vien Python da day du.
)

:: 5. Cau hinh .env va Database
set "ENV_FILE=%PROJECT_ROOT%.env"
set "ENV_EXAMPLE=%PROJECT_ROOT%.env.example"

if not exist "%ENV_FILE%" (
    if exist "%ENV_EXAMPLE%" (
        echo [4/5] Khoi tao file .env tu .env.example ...
        copy "%ENV_EXAMPLE%" "%ENV_FILE%" >nul
    )
)

if "%LOCAL_SQLITE%"=="1" (
    echo [4/5] Che do SQLite: Su dung co so du lieu cuc bo dvc_local.db.
    set "DATABASE_URL=sqlite:///./dvc_local.db"
    echo       DATABASE_URL = !DATABASE_URL!
) else (
    set "DOCKER_READY=0"
    docker --version >nul 2>&1
    if not errorlevel 1 (
        docker info >nul 2>&1
        if not errorlevel 1 set "DOCKER_READY=1"
    )

    if "!DOCKER_READY!"=="1" (
        echo [4/5] Che do PostgreSQL: Dang khoi dong PostgreSQL 16 bang Docker Compose ...
        docker compose up -d postgres
        echo       Dang cho PostgreSQL san sang...
        set "PG_READY=0"
        for /l %%i in (1, 1, 20) do (
            if "!PG_READY!"=="0" (
                docker compose exec -T postgres pg_isready -U dvc_user -d dvc_vietnam >nul 2>&1
                if not errorlevel 1 set "PG_READY=1"
                if "!PG_READY!"=="0" ping 127.0.0.1 -n 2 >nul
            )
        )
        if "%DATABASE_URL%"=="" (
            set "DATABASE_URL=postgresql://dvc_user:dvc_secret_2026@localhost:5432/dvc_vietnam"
        )
        echo       PostgreSQL da san sang: !DATABASE_URL!
    ) else (
        echo [4/5] Khong phat hien Docker dang chay -^> Tu dong chuyen sang SQLite cuc bo [dvc_local.db].
        echo       [Bat Docker Desktop va chay lai run_develop.bat de dung PostgreSQL 16]
        set "DATABASE_URL=sqlite:///./dvc_local.db"
        echo       DATABASE_URL = !DATABASE_URL!
    )
)

:: 6. Dong bo thu muc procedures/*.md va khoi chay Uvicorn
echo [5/5] Dong bo thu muc procedures/*.md va khoi chay server...
"%VENV_PYTHON%" scripts\sync_md.py
if errorlevel 1 (
    echo [CANH BAO] Qua trinh dong bo co loi, tiep tuc khoi dong server...
)

echo.
echo   ============================================================
echo   Website dang chay tai : http://127.0.0.1:%PORT%
echo   Trang cap nhat .md    : http://127.0.0.1:%PORT%/cap-nhat
echo   Nhan Ctrl+C de dung server.
echo   ============================================================
echo.

"%VENV_PYTHON%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port %PORT%
if errorlevel 1 (
    pause
)
