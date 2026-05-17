@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

:: ============================================================
:: Luymas AI - Windows Quick Start
:: ============================================================

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Colors
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "CYAN=[36m"
set "BOLD=[1m"
set "DIM=[2m"
set "RESET=[0m"

echo.
echo %CYAN%%BOLD%  Luymas AI - Quick Start%RESET%
echo.

:: ── Check if virtual environment exists ──────────────────────
if not exist "%SCRIPT_DIR%\venv\Scripts\activate.bat" (
    echo %RED%✗ Virtual environment not found!%RESET%
    echo.
    echo   %CYAN%→ Run install.bat first to set up the environment.%RESET%
    echo.
    pause
    exit /b 1
)

:: ── Activate virtual environment ─────────────────────────────
call "%SCRIPT_DIR%\venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo %RED%✗ Failed to activate virtual environment%RESET%
    echo.
    pause
    exit /b 1
)

:: ── Change to project directory ──────────────────────────────
cd /d "%SCRIPT_DIR%"

:: ── Run the launcher ─────────────────────────────────────────
echo %GREEN%✓ Starting Luymas AI...%RESET%
echo.

python launcher.py

:: ── Handle errors ────────────────────────────────────────────
if %errorlevel% neq 0 (
    echo.
    echo %RED%✗ Luymas AI exited with error code %errorlevel%%RESET%
    echo.
    echo   %DIM%Common fixes:%RESET%
    echo   %DIM%  - Run install.bat to reinstall dependencies%RESET%
    echo   %DIM%  - Make sure Ollama is running: ollama serve%RESET%
    echo   %DIM%  - Check logs in: logs\luymas.log%RESET%
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo %CYAN%Au revoir !%RESET%
echo.
