@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

:: ============================================================
:: Luymas AI - Windows Installation Script
:: Multi-Agent AI System with WhatsApp/Telegram Integration
:: ============================================================

:: Colors via ANSI escape codes (Windows 10+)
set "RED=[31m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "MAGENTA=[35m"
set "CYAN=[36m"
set "WHITE=[37m"
set "BOLD=[1m"
set "DIM=[2m"
set "RESET=[0m"

:: Script directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: ============================================================
:: BANNER
:: ============================================================
echo.
echo %CYAN%%BOLD%╔══════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%%BOLD%║                                                          ║%RESET%
echo %CYAN%%BOLD%║            %WHITE%⭐ LUYMAS AI - Installation ⭐%CYAN%                   ║%RESET%
echo %CYAN%%BOLD%║                                                          ║%RESET%
echo %CYAN%%BOLD%║      %WHITE%Multi-Agent AI System with WhatsApp/Telegram%CYAN%          ║%RESET%
echo %CYAN%%BOLD%║                                                          ║%RESET%
echo %CYAN%%BOLD%║  %YELLOW%Bienvenue dans l'installateur de Luymas AI !%CYAN%               ║%RESET%
echo %CYAN%%BOLD%║  %YELLOW%Votre equipe d'agents intelligents vous attend.%CYAN%             ║%RESET%
echo %CYAN%%BOLD%║                                                          ║%RESET%
echo %CYAN%%BOLD%╚══════════════════════════════════════════════════════════╝%RESET%
echo.

:: ============================================================
:: STEP 1: CHECK PYTHON
:: ============================================================
echo.
echo %BLUE%%BOLD%━━━ STEP 1: Python Check ━━━%RESET%
echo.

:: Check if python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   %RED%✗ Python is not installed or not in PATH%RESET%
    echo.
    echo   %CYAN%→ Please install Python 3.10 or later:%RESET%
    echo     https://www.python.org/downloads/
    echo.
    echo   %DIM%Make sure to check "Add Python to PATH" during installation.%RESET%
    echo.
    pause
    exit /b 1
)

:: Check Python version (3.10+)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VERSION=%%v"
for /f "tokens=1,2 delims=." %%a in ("%PY_VERSION%") do (
    set "PY_MAJOR=%%a"
    set "PY_MINOR=%%b"
)

if %PY_MAJOR% lss 3 (
    echo   %RED%✗ Python 3.10+ required, found %PY_VERSION%%RESET%
    echo   %CYAN%→ Download: https://www.python.org/downloads/%RESET%
    pause
    exit /b 1
)
if %PY_MAJOR% equ 3 if %PY_MINOR% lss 10 (
    echo   %RED%✗ Python 3.10+ required, found %PY_VERSION%%RESET%
    echo   %CYAN%→ Download: https://www.python.org/downloads/%RESET%
    pause
    exit /b 1
)

echo   %GREEN%✓ Python %PY_VERSION% found%RESET%

:: ============================================================
:: STEP 2: CREATE VIRTUAL ENVIRONMENT
:: ============================================================
echo.
echo %BLUE%%BOLD%━━━ STEP 2: Virtual Environment ━━━%RESET%
echo.

if exist "%SCRIPT_DIR%\venv\Scripts\activate.bat" (
    echo   %GREEN%✓ Virtual environment already exists%RESET%
) else (
    echo   %CYAN%→ Creating virtual environment...%RESET%
    python -m venv "%SCRIPT_DIR%\venv"
    if %errorlevel% neq 0 (
        echo   %RED%✗ Failed to create virtual environment%RESET%
        pause
        exit /b 1
    )
    echo   %GREEN%✓ Virtual environment created%RESET%
)

:: Activate the venv
call "%SCRIPT_DIR%\venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo   %RED%✗ Failed to activate virtual environment%RESET%
    pause
    exit /b 1
)
echo   %GREEN%✓ Virtual environment activated%RESET%

:: Upgrade pip
echo   %CYAN%→ Upgrading pip...%RESET%
python -m pip install --upgrade pip --quiet 2>nul

:: ============================================================
:: STEP 3: INSTALL PYTHON DEPENDENCIES
:: ============================================================
echo.
echo %BLUE%%BOLD%━━━ STEP 3: Python Dependencies ━━━%RESET%
echo.

if not exist "%SCRIPT_DIR%\requirements.txt" (
    echo   %RED%✗ requirements.txt not found in %SCRIPT_DIR%%RESET%
    echo   %CYAN%→ Make sure you are running this from the Luymas AI directory%RESET%
    pause
    exit /b 1
)

echo   %CYAN%→ Installing Python packages (this may take a few minutes)...%RESET%
pip install -r "%SCRIPT_DIR%\requirements.txt" --quiet 2>nul
if %errorlevel% neq 0 (
    echo   %YELLOW%⚠ Some packages failed with quiet mode. Retrying with verbose output...%RESET%
    pip install -r "%SCRIPT_DIR%\requirements.txt" 2>nul
    if %errorlevel% neq 0 (
        echo   %YELLOW%⚠ Some dependencies may have issues. Check requirements.txt.%RESET%
    ) else (
        echo   %GREEN%✓ Python dependencies installed%RESET%
    )
) else (
    echo   %GREEN%✓ Python dependencies installed%RESET%
)

:: ============================================================
:: STEP 4: CHECK / INSTALL OLLAMA
:: ============================================================
echo.
echo %BLUE%%BOLD%━━━ STEP 4: Ollama Installation ━━━%RESET%
echo.

where ollama >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%o in ('ollama --version 2^>^&1') do set "OLLAMA_VER=%%o"
    echo   %GREEN%✓ Ollama already installed: !OLLAMA_VER!%RESET%
) else (
    echo   %YELLOW%⚠ Ollama is not installed%RESET%
    echo.
    echo   %CYAN%→ Downloading Ollama for Windows...%RESET%
    echo     %DIM%https://ollama.com/download/windows%RESET%
    echo.

    :: Try to download using PowerShell
    set "OLLAMA_INSTALLER=%TEMP%\OllamaSetup.exe"
    echo   %CYAN%→ Downloading Ollama installer...%RESET%
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'}" 2>nul
    if exist "%TEMP%\OllamaSetup.exe" (
        echo   %CYAN%→ Launching Ollama installer...%RESET%
        echo     %DIM%Please complete the installation, then re-run this script.%RESET%
        start "" "%TEMP%\OllamaSetup.exe"
        echo.
        echo   %YELLOW%⚠ After Ollama is installed, please run this script again.%RESET%
        pause
        exit /b 0
    ) else (
        echo   %RED%✗ Could not download Ollama automatically%RESET%
        echo.
        echo   %CYAN%→ Please install Ollama manually:%RESET%
        echo     1. Visit https://ollama.com/download/windows
        echo     2. Download and run the installer
        echo     3. Re-run this script
        echo.
        pause
        exit /b 1
    )
)

:: ============================================================
:: STEP 5: DOWNLOAD AI MODELS
:: ============================================================
echo.
echo %BLUE%%BOLD%━━━ STEP 5: AI Model Downloads ━━━%RESET%
echo.

echo   %CYAN%→ Checking available models...%RESET%
echo.

:: Make sure Ollama server is running
echo   %CYAN%→ Starting Ollama server (if not already running)...%RESET%
start /b "" ollama serve >nul 2>&1
timeout /t 3 /nobreak >nul 2>&1

:: Define models: tag|description|size
set "MODEL_COUNT=5"
set "MODEL_1_TAG=deepseek-r1:8b"
set "MODEL_1_DESC=Reasoning (8B params, fits 8GB RAM)"
set "MODEL_1_SIZE=~4.7GB"

set "MODEL_2_TAG=qwen2.5-coder:7b"
set "MODEL_2_DESC=Code generation (7B params, fits 8GB RAM)"
set "MODEL_2_SIZE=~4.5GB"

set "MODEL_3_TAG=gemma3:4b"
set "MODEL_3_DESC=Lightweight assistant (4B params, minimal RAM)"
set "MODEL_3_SIZE=~2.6GB"

set "MODEL_4_TAG=z-image-turbo"
set "MODEL_4_DESC=Image generation (experimental)"
set "MODEL_4_SIZE=~3.8GB"

set "MODEL_5_TAG=llama3.2:3b"
set "MODEL_5_DESC=Quick tasks (3B params, very fast)"
set "MODEL_5_SIZE=~2.0GB"

:: Check each model and prompt for download
for /l %%i in (1,1,%MODEL_COUNT%) do (
    set "TAG=!MODEL_%%i_TAG!"
    set "DESC=!MODEL_%%i_DESC!"
    set "SIZE=!MODEL_%%i_SIZE!"

    echo.
    echo   %WHITE%Model: !TAG!%RESET%
    echo   %DIM%  !DESC! (!SIZE!)%RESET%

    :: Check if model is already installed
    ollama list 2>nul | findstr /c:"!TAG!" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   %GREEN%✓ Already installed%RESET%
    ) else (
        set /p "DOWNLOAD=  Download !TAG!? (Y/N): "
        if /i "!DOWNLOAD!"=="Y" (
            echo   %CYAN%→ Pulling !TAG!... (this may take a while)%RESET%
            ollama pull !TAG!
            if !errorlevel! equ 0 (
                echo   %GREEN%✓ !TAG! installed successfully%RESET%
            ) else (
                echo   %RED%✗ Failed to download !TAG!%RESET%
                echo   %DIM%  You can try later: ollama pull !TAG!%RESET%
            )
        ) else (
            echo   %DIM%  Skipped. Install later: ollama pull !TAG!%RESET%
        )
    )
)

:: ============================================================
:: STEP 6: GENERATE .env FROM .env.example
:: ============================================================
echo.
echo.
echo %BLUE%%BOLD%━━━ STEP 6: Environment Configuration ━━━%RESET%
echo.

if exist "%SCRIPT_DIR%\.env" (
    echo   %GREEN%✓ .env file already exists%RESET%
) else if exist "%SCRIPT_DIR%\.env.example" (
    copy "%SCRIPT_DIR%\.env.example" "%SCRIPT_DIR%\.env" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   %GREEN%✓ Created .env from .env.example%RESET%
    ) else (
        echo   %YELLOW%⚠ Failed to copy .env.example to .env%RESET%
    )
) else (
    echo   %YELLOW%⚠ .env.example not found, creating minimal .env%RESET%
    (
        echo # Luymas AI Environment
        echo OLLAMA_HOST=http://localhost:11434
        echo LUYMAS_ENV=sandbox
        echo LUYMAS_LOG_LEVEL=INFO
        echo LUYMAS_HARDWARE_TIER=1
        echo LUYMAS_DATA_DIR=./data
        echo LUYMAS_OUTPUT_DIR=./output
        echo LUYMAS_MAX_CONCURRENT_AGENTS=1
    ) > "%SCRIPT_DIR%\.env"
    echo   %GREEN%✓ Created minimal .env%RESET%
)

:: ============================================================
:: STEP 7: CREATE DIRECTORIES
:: ============================================================
echo.
echo %BLUE%%BOLD%━━━ STEP 7: Directory Structure ━━━%RESET%
echo.

for %%d in (models logs data "design\assets") do (
    if not exist "%SCRIPT_DIR%\%%d" (
        mkdir "%SCRIPT_DIR%\%%d" 2>nul
        if exist "%SCRIPT_DIR%\%%d" (
            echo   %GREEN%✓ Created directory: %%d\%RESET%
        ) else (
            echo   %RED%✗ Failed to create: %%d\%RESET%
        )
    ) else (
        echo   %GREEN%✓ Directory exists: %%d\%RESET%
    )
)

:: ============================================================
:: STEP 8: FINAL VERIFICATION
:: ============================================================
echo.
echo %BLUE%%BOLD%━━━ STEP 8: Verification ━━━%RESET%
echo.

set "VERIFY_ERRORS=0"

:: Check Python in venv
python -c "import sys; sys.exit(0)" >nul 2>&1
if %errorlevel% equ 0 (
    echo   %GREEN%✓ Python is working in virtual environment%RESET%
) else (
    echo   %RED%✗ Python not working in virtual environment%RESET%
    set /a VERIFY_ERRORS+=1
)

:: Check critical Python packages
python -c "import ollama; import yaml; import flask; import dotenv; import aiohttp" >nul 2>&1
if %errorlevel% equ 0 (
    echo   %GREEN%✓ Core Python dependencies OK%RESET%
) else (
    echo   %YELLOW%⚠ Some Python dependencies may be missing%RESET%
    set /a VERIFY_ERRORS+=1
)

:: Check Ollama
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo   %GREEN%✓ Ollama is installed%RESET%
) else (
    echo   %YELLOW%⚠ Ollama not found in PATH%RESET%
    set /a VERIFY_ERRORS+=1
)

:: Check .env
if exist "%SCRIPT_DIR%\.env" (
    echo   %GREEN%✓ .env configured%RESET%
) else (
    echo   %RED%✗ .env file missing%RESET%
    set /a VERIFY_ERRORS+=1
)

:: Check directories
for %%d in (models logs data "design\assets") do (
    if exist "%SCRIPT_DIR%\%%d" (
        echo   %GREEN%✓ Directory %%d\ OK%RESET%
    ) else (
        echo   %YELLOW%⚠ Directory %%d\ missing%RESET%
        set /a VERIFY_ERRORS+=1
    )
)

:: Check Studio files
if exist "%SCRIPT_DIR%\studio\index.html" (
    echo   %GREEN%✓ Studio web interface found%RESET%
) else (
    echo   %YELLOW%⚠ Studio web interface not found%RESET%
)

:: Check config files
if exist "%SCRIPT_DIR%\config\agents.yaml" (
    echo   %GREEN%✓ Agent configuration found%RESET%
) else (
    echo   %YELLOW%⚠ Agent configuration not found%RESET%
)

if exist "%SCRIPT_DIR%\config\models.yaml" (
    echo   %GREEN%✓ Model configuration found%RESET%
) else (
    echo   %YELLOW%⚠ Model configuration not found%RESET%
)

:: ============================================================
:: COMPLETION
:: ============================================================
echo.
echo %CYAN%%BOLD%╔══════════════════════════════════════════════════════════╗%RESET%
if %VERIFY_ERRORS% equ 0 (
    echo %GREEN%%BOLD%║            🚀 LUYMAS AI IS READY! 🚀                     ║%RESET%
) else (
    echo %YELLOW%%BOLD%║   ⚠ LUYMAS AI installed with %VERIFY_ERRORS% warning(s)                  ║%RESET%
)
echo %CYAN%%BOLD%╚══════════════════════════════════════════════════════════╝%RESET%
echo.
echo   To start Luymas AI:
echo.
echo     %GREEN%%BOLD%launcher.bat%RESET%
echo.
echo   Or manually:
echo.
echo     %DIM%venv\Scripts\activate.bat%RESET%
echo     %DIM%python launcher.py%RESET%
echo.
echo   To add more models later:
echo.
echo     %DIM%ollama pull ^<model-name^>%RESET%
echo.
echo   Documentation: https://github.com/ebrill82/luymas-ai
echo.

pause
