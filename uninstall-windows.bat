@echo off
setlocal

echo.
echo ============================================================
echo      Iris Meteo Beacon - Windows Uninstaller
echo ============================================================
echo.

:: Confirm with user
set /p CONFIRM="This will delete EVERYTHING (code, config, services). Are you sure? (y/n): "
if /i "%CONFIRM%" neq "y" (
    echo Uninstall cancelled.
    pause
    exit /b
)

:: Terminate running process
echo [1/4] Stopping Iris Meteo Beacon processes...
:: Try to stop via Window Title first (if running in a visible window)
taskkill /F /FI "WINDOWTITLE eq Starting Iris Meteo Beacon*" /T >nul 2>&1
:: Use PowerShell to find and stop the process by command line
powershell -Command "Get-CimInstance Win32_Process -Filter \"CommandLine LIKE '%%main.py%%'\" | Stop-Process -Force" >nul 2>&1

:: Remove Autostart
echo [2/4] Removing Autostart script...
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
if exist "%STARTUP_DIR%\iris_meteo_beacon.bat" (
    del "%STARTUP_DIR%\iris_meteo_beacon.bat"
    echo   - Removed from Startup folder.
)

:: Remove Start batch file
echo [3/4] Removing start_beacon.bat...
if exist "start_beacon.bat" (
    del "start_beacon.bat"
)

echo [4/4] Finalizing cleanup...
echo.
echo ============================================================
echo   Uninstall almost complete! 
echo   This window will close and the project folder will be deleted.
echo ============================================================
echo.

:: Small delay to ensure files are closed
timeout /t 3 /nobreak >nul

:: Self-deletion logic:
:: 1. Change directory to parent
:: 2. Start a background process that waits, then deletes the folder
:: 3. Exit the current script
cd ..
set "TARGET_DIR=%~dp0"
:: Remove trailing backslash if present
if "%TARGET_DIR:~-1%"=="\" set "TARGET_DIR=%TARGET_DIR:~0,-1%"

start /b "" cmd /c "timeout /t 2 /nobreak && rd /s /q \"%TARGET_DIR%\""
exit
