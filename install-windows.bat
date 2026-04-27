@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo      Iris Meteo Beacon - Windows Installation Script
echo ============================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and check "Add Python to PATH".
    pause
    exit /b 1
)

:: Create Virtual Environment
echo [1/3] Creating Virtual Environment (.venv)...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

:: Install Dependencies
echo [2/3] Installing dependencies from requirements.txt...
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Create a Start shortcut script
echo [3/4] Creating start_beacon.bat...
echo @echo off > start_beacon.bat
echo echo Starting Iris Meteo Beacon... >> start_beacon.bat
echo .venv\Scripts\python main.py >> start_beacon.bat
echo if %%errorlevel%% neq 0 pause >> start_beacon.bat

:: Enable Autostart by default
echo [4/4] Enabling Autostart on Boot...
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
echo @echo off > "%STARTUP_DIR%\iris_meteo_beacon.bat"
echo cd /d "%CD%" >> "%STARTUP_DIR%\iris_meteo_beacon.bat"
echo start "" /min ".venv\Scripts\python" main.py >> "%STARTUP_DIR%\iris_meteo_beacon.bat"

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo To start the beacon, run: start_beacon.bat
echo Access the Dashboard at: http://localhost:1982
echo.
pause
start start_beacon.bat
exit
