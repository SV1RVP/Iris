import os
import sys
import platform
import logging
import subprocess

def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def check_status():
    """Checks if autostart is currently enabled."""
    system = platform.system()
    if system == "Windows":
        startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        bat_path = os.path.join(startup_folder, "iris_meteo_beacon.bat")
        return os.path.exists(bat_path)
    elif system == "Linux":
        # 1. Check for .desktop file (user-level autostart)
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "iris_meteo_beacon.desktop")
        if os.path.exists(desktop_file):
            return True
            
        # 2. Check for systemd service (system-level autostart used by installer)
        try:
            # We check if the service is enabled. Note: iris-meteo.service is the name used in install-linux.sh
            result = subprocess.run(
                ["systemctl", "is-enabled", "iris-meteo.service"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip() == "enabled":
                return True
        except Exception:
            pass
            
    return False

def enable_autostart():
    """Enables autostart for the current OS."""
    system = platform.system()
    project_root = get_project_root()
    main_py = os.path.join(project_root, "main.py")
    
    try:
        if system == "Windows":
            startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            bat_path = os.path.join(startup_folder, "iris_meteo_beacon.bat")
            
            # Use the current python executable
            python_exe = sys.executable
            
            with open(bat_path, "w") as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{project_root}"\n')
                f.write(f'"{python_exe}" "{main_py}"\n')
            return True, "Autostart enabled (Batch file created in Startup folder)."
            
        elif system == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            if not os.path.exists(autostart_dir):
                os.makedirs(autostart_dir)
            
            desktop_file = os.path.join(autostart_dir, "iris_meteo_beacon.desktop")
            content = f"""[Desktop Entry]
Type=Application
Exec={sys.executable} {main_py}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Iris Meteo Beacon
Comment=Start Iris Meteo Beacon on login
"""
            with open(desktop_file, "w") as f:
                f.write(content)
            return True, "Autostart enabled (.desktop file created in ~/.config/autostart)."
            
        return False, f"Unsupported system: {system}"
    except Exception as e:
        logging.error(f"Failed to enable autostart: {e}")
        return False, str(e)

def disable_autostart():
    """Disables autostart."""
    system = platform.system()
    try:
        if system == "Windows":
            startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            bat_path = os.path.join(startup_folder, "iris_meteo_beacon.bat")
            if os.path.exists(bat_path):
                os.remove(bat_path)
            return True, "Autostart disabled (Batch file removed)."
        elif system == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            desktop_file = os.path.join(autostart_dir, "iris_meteo_beacon.desktop")
            if os.path.exists(desktop_file):
                os.remove(desktop_file)
            return True, "Autostart disabled (.desktop file removed)."
        return False, f"Unsupported system: {system}"
    except Exception as e:
        logging.error(f"Failed to disable autostart: {e}")
        return False, str(e)
