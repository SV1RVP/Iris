import os
import sys
import json
import logging
import platform
import subprocess
import requests
import zipfile
import shutil
import time

VERSION_FILE = 'version.json'
GITLAB_VERSION_URL = 'https://gitlab.com/SV1RVP/iris-meteo-beacon/-/raw/master/version.json'
GITLAB_ZIP_URL = 'https://gitlab.com/SV1RVP/iris-meteo-beacon/-/archive/master/iris-meteo-beacon-master.zip'

def get_local_version():
    """Reads the current version from version.json."""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error reading local version: {e}")
    return {"version": "0.0.0", "commit": "unknown"}

def get_remote_version():
    """Fetches the latest version from GitLab."""
    try:
        response = requests.get(GITLAB_VERSION_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.error(f"Error fetching remote version: {e}")
    return None

def check_for_updates():
    """Compares local version with remote version."""
    local = get_local_version()
    remote = get_remote_version()
    
    if not remote:
        return {"status": "error", "message": "Could not check for updates."}
    
    # Check if we are in a Git repo
    is_git = os.path.exists('.git')
    
    update_available = False
    if is_git:
        # For git, we use the commit hash if available, or just check git directly
        try:
            subprocess.run(["git", "fetch"], capture_output=True)
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/master"],
                capture_output=True, text=True
            )
            count = int(result.stdout.strip())
            update_available = count > 0
        except:
            # Fallback to version comparison if git fails
            update_available = remote['version'] != local['version']
    else:
        update_available = remote['version'] != local['version']
        
    return {
        "status": "success",
        "update_available": update_available,
        "local_version": local['version'],
        "remote_version": remote['version'],
        "is_git": is_git
    }

def flush_logs():
    """Forces all logging handlers to write their buffers to disk."""
    for handler in logging.getLogger().handlers:
        handler.flush()

def run_update():
    """Starts the update process."""
    is_git = os.path.exists('.git')
    system = platform.system()
    
    logging.info("--- Starting Update Request ---")
    flush_logs()
    
    # Check for write permissions in current directory
    if not os.access('.', os.W_OK):
        msg = f"Insufficient permissions to write in {os.getcwd()}. Please run as Administrator/Sudo."
        logging.error(msg)
        return False, msg

    if is_git:
        logging.info("Starting Git update (pulling latest commits)...")
        flush_logs()
        try:
            # Simple git pull
            subprocess.run(["git", "pull"], check=True)
            
            if system == "Linux":
                # Systemd service has Restart=always, so just exit
                logging.info("Update complete. Exiting process. Systemd will restart the service automatically...")
                flush_logs()
                time.sleep(1)
                os._exit(0)
            else:
                logging.info("Git pull complete. Manual restart required on Windows Git installations.")
                return True, "Update applied via Git. Please restart start_beacon.bat manually."
        except Exception as e:
            logging.error(f"Git update failed: {e}")
            return False, f"Git update failed: {e}"
            
    else:
        # ZIP-based update for non-git users
        logging.info("Starting ZIP update process (Universal mode)...")
        flush_logs()
        try:
            # 1. Download ZIP
            logging.info(f"Connecting to GitLab: {GITLAB_ZIP_URL} ...")
            flush_logs()
            resp = requests.get(GITLAB_ZIP_URL, stream=True, timeout=30)
            resp.raise_for_status() 
            
            zip_path = "update.zip"
            with open(zip_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info("Download successful. ZIP file saved.")
            flush_logs()
            
            if system == "Windows":
                logging.info("Generating Windows Update Helper script...")
                flush_logs()
                create_windows_updater_script(zip_path)
                
                logging.info("Launching updater and exiting main application...")
                flush_logs()
                subprocess.Popen(["cmd", "/c", "start", "update_helper.bat"], shell=True)
                time.sleep(1)
                os._exit(0) 
            else:
                # Linux ZIP (unlikely but possible)
                logging.info("Update complete. Exiting process. Systemd will restart the service automatically...")
                flush_logs()
                time.sleep(1)
                os._exit(0)
                
        except Exception as e:
            err_msg = f"ZIP update failed: {e}"
            logging.error(err_msg)
            flush_logs()
            return False, err_msg

def create_windows_updater_script(zip_path):
    """Creates a temporary batch file to perform the update on Windows."""
    script_content = f"""@echo off
setlocal enabledelayedexpansion
echo ============================================================
echo         Iris Meteo Beacon - Windows Updater
echo ============================================================
echo Waiting for main process to close...
timeout /t 3 /nobreak > nul

echo Extracting updates...
if exist "_temp_update" rmdir /s /q "_temp_update"
powershell -Command "Expand-Archive -Path '{zip_path}' -DestinationPath '_temp_update' -Force"

set "EXT_DIR="
for /d %%d in ("_temp_update\\*") do (
    set "EXT_DIR=%%d"
)

if defined EXT_DIR (
    echo Found update files in: !EXT_DIR!
    echo Moving files...
    xcopy /s /e /y /q "!EXT_DIR!\\*" "."
) else (
    echo Error: Could not find extracted folder.
    pause
    exit
)

echo Update Complete!
echo Restarting Iris Meteo Beacon...
start start_beacon.bat
echo Cleaning up...
del "{zip_path}"
rmdir /s /q "_temp_update"
(goto) 2>nul & del "update_helper.bat" & exit
"""
    with open("update_helper.bat", "w") as f:
        f.write(script_content)
