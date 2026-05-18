@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

:: ============================================================
:: Luymas AI — Script de Démarrage Portable (Clé USB)
:: Détecte et installe Ollama si nécessaire, configure les
:: chemins relatifs, démarre le système et ouvre le navigateur.
:: ============================================================

:: Couleurs ANSI (Windows 10+)
set "GREEN=[32m"
set "YELLOW=[33m"
set "CYAN=[36m"
set "RED=[31m"
set "BOLD=[1m"
set "DIM=[2m"
set "RESET=[0m"

:: Déterminer le chemin du script (racine de la clé USB)
set "USB_ROOT=%~dp0"
set "USB_ROOT=%USB_ROOT:~0,-1%"
set "PROJECT_DIR=%USB_ROOT%\luymas-ai"

echo.
echo %CYAN%%BOLD%╔══════════════════════════════════════════════╗%RESET%
echo %CYAN%%BOLD%║    💾 LUYMAS AI - DÉMARRAGE PORTABLE         ║%RESET%
echo %CYAN%%BOLD%╚══════════════════════════════════════════════╝%RESET%
echo.

:: ============================================================
:: ÉTAPE 1 : VÉRIFIER QUE LE PROJET EXISTE
:: ============================================================
echo %CYAN%[1/6] Vérification du projet...%RESET%
if not exist "%PROJECT_DIR%\launcher.py" (
    echo   %RED%✗ Fichiers du projet introuvables sur la clé USB%RESET%
    echo   %DIM%  Chemin vérifié : %PROJECT_DIR%%RESET%
    echo.
    echo   Veuillez exécuter core/usb_builder.py pour préparer la clé.
    pause
    exit /b 1
)
echo   %GREEN%✓ Projet trouvé%RESET%

:: ============================================================
:: ÉTAPE 2 : VÉRIFIER / INSTALLER OLLAMA
:: ============================================================
echo.
echo %CYAN%[2/6] Vérification d'Ollama...%RESET%

where ollama >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%o in ('ollama --version 2^>^&1') do set "OLLAMA_VER=%%o"
    echo   %GREEN%✓ Ollama déjà installé : !OLLAMA_VER!%RESET%
    goto :ollama_found
)

:: Ollama absent — vérifier l'installateur portable sur la clé
echo   %YELLOW%⚠ Ollama non trouvé sur ce système%RESET%

if exist "%USB_ROOT%\ollama_portable\OllamaSetup.exe" (
    echo   %CYAN%→ Installateur trouvé sur la clé USB%RESET%
    echo   %CYAN%→ Lancement de l'installation...%RESET%
    echo.
    echo   %DIM%  ⚠ Veuillez compléter l'installation, puis relancez ce script.%RESET%
    start "" "%USB_ROOT%\ollama_portable\OllamaSetup.exe"
    echo.
    echo   %YELLOW%  Après l'installation, relancez start.bat%RESET%
    pause
    exit /b 0
)

:: Tentative de téléchargement automatique
echo   %CYAN%→ Téléchargement automatique d'Ollama...%RESET%
echo   %DIM%  Depuis https://ollama.com/download%RESET%

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host '  Téléchargement en cours...'; Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'}" 2>nul

if exist "%TEMP%\OllamaSetup.exe" (
    echo   %GREEN%✓ Ollama téléchargé%RESET%
    echo   %CYAN%→ Lancement de l'installation...%RESET%
    start "" "%TEMP%\OllamaSetup.exe"
    echo.
    echo   %YELLOW%  Après l'installation, relancez start.bat%RESET%
    pause
    exit /b 0
) else (
    echo   %RED%✗ Impossible de télécharger Ollama automatiquement%RESET%
    echo.
    echo   %CYAN%→ Installez Ollama manuellement :%RESET%
    echo     1. Visitez https://ollama.com/download/windows
    echo     2. Téléchargez et installez
    echo     3. Relancez ce script
    echo.
    pause
    exit /b 1
)

:ollama_found

:: ============================================================
:: ÉTAPE 3 : DÉMARRER OLLAMA
:: ============================================================
echo.
echo %CYAN%[3/6] Démarrage d'Ollama...%RESET%

:: Vérifier si Ollama tourne déjà
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo   %GREEN%✓ Ollama est déjà en cours d'exécution%RESET%
    goto :ollama_running
)

:: Démarrer Ollama en arrière-plan
echo   %CYAN%→ Démarrage du serveur Ollama...%RESET%
start /b "" ollama serve >nul 2>&1

:: Attendre qu'Ollama soit prêt
set "RETRIES=0"
:wait_ollama
timeout /t 2 /nobreak >nul 2>&1
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo   %GREEN%✓ Ollama démarré avec succès%RESET%
    goto :ollama_running
)
set /a RETRIES+=1
if %RETRIES% lss 15 (
    echo   %DIM%  En attente d'Ollama... (%RETRIES%/15)%RESET%
    goto :wait_ollama
)

echo   %RED%✗ Ollama n'a pas démarré dans les 30 secondes%RESET%
echo   %DIM%  Essayez de démarrer Ollama manuellement : ollama serve%RESET%
pause
exit /b 1

:ollama_running

:: ============================================================
:: ÉTAPE 4 : LISTER LES MODÈLES DISPONIBLES
:: ============================================================
echo.
echo %CYAN%[4/6] Modèles disponibles :%RESET%
echo.
ollama list 2>nul
echo.

:: ============================================================
:: ÉTAPE 5 : CONFIGURER LES CHEMINS RELATIFS
:: ============================================================
echo.
echo %CYAN%[5/6] Configuration de l'environnement...%RESET%

:: Variables d'environnement avec chemins relatifs
set "OLLAMA_HOST=http://localhost:11434"
set "LUYMAS_DATA_DIR=%PROJECT_DIR%\data"
set "LUYMAS_OUTPUT_DIR=%PROJECT_DIR%\output"
set "LUYMAS_LOG_LEVEL=INFO"
set "LUYMAS_ENV=portable"

:: Créer les dossiers s'ils n'existent pas
if not exist "%LUYMAS_DATA_DIR%" mkdir "%LUYMAS_DATA_DIR%"
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs%"
if not exist "%PROJECT_DIR%\output" mkdir "%PROJECT_DIR%\output%"

:: Créer .env minimal si absent
if not exist "%PROJECT_DIR%\.env" (
    (
        echo # Luymas AI - Environnement Portable
        echo OLLAMA_HOST=http://localhost:11434
        echo LUYMAS_ENV=portable
        echo LUYMAS_LOG_LEVEL=INFO
        echo LUYMAS_DATA_DIR=%LUYMAS_DATA_DIR%
        echo LUYMAS_OUTPUT_DIR=%PROJECT_DIR%\output
        echo LUYMAS_MAX_CONCURRENT_AGENTS=1
    ) > "%PROJECT_DIR%\.env"
    echo   %GREEN%✓ Fichier .env créé%RESET%
) else (
    echo   %GREEN%✓ Fichier .env existant%RESET%
)

echo   %GREEN%✓ Environnement configuré%RESET%

:: ============================================================
:: ÉTAPE 6 : LANCER LUYMAS AI
:: ============================================================
echo.
echo %CYAN%[6/6] Lancement de Luymas AI...%RESET%
echo.

cd /d "%PROJECT_DIR%"

:: Vérifier Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    :: Essayer Python portable sur la clé
    if exist "%USB_ROOT%\python_portable\python\python.exe" (
        set "PATH=%USB_ROOT%\python_portable\python;%PATH%"
    ) else (
        echo   %RED%✗ Python non trouvé%RESET%
        echo   %CYAN%→ Installez Python 3.10+ : https://www.python.org/downloads/%RESET%
        pause
        exit /b 1
    )
)

:: Lancer Luymas AI
echo   %GREEN%🚀 Luymas AI démarre !%RESET%
echo   %DIM%  Le Studio s'ouvrira dans votre navigateur.%RESET%
echo   %DIM%  Appuyez sur Ctrl+C pour arrêter.%RESET%
echo.

python launcher.py

:: Retour au répertoire d'origine
cd /d "%USB_ROOT%"
echo.
echo   %CYAN%Au revoir ! À bientôt sur Luymas AI.%RESET%
pause
