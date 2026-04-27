@echo off
echo Starting Iris Meteo Beacon...
.venv\Scripts\python main.py
if %errorlevel% neq 0 pause
