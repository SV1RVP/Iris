#!/bin/bash
# Iris Meteo Beacon - Linux Uninstaller
# Author: Alexandros - Ermis Tsourapas, SV1RVP

echo ""
echo "============================================================"
echo "      Iris Meteo Beacon - Linux Uninstaller"
echo "============================================================"
echo ""

# Confirm with user
read -p "This will delete EVERYTHING (code, config, services). Are you sure? (y/n): [y/N] " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

SERVICE_NAME="iris-meteo.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

# Stop and Disable service
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "[1/4] Stopping $SERVICE_NAME..."
    sudo systemctl stop $SERVICE_NAME
fi

if systemctl is-enabled --quiet $SERVICE_NAME; then
    echo "[2/4] Disabling $SERVICE_NAME..."
    sudo systemctl disable $SERVICE_NAME
fi

# Remove service file
if [ -f "$SERVICE_FILE" ]; then
    echo "[3/4] Removing service file $SERVICE_FILE..."
    sudo rm "$SERVICE_FILE"
    sudo systemctl daemon-reload
    echo "  - Systemd service removed and reloaded."
fi

# Remove directory
echo "[4/4] Removing project files..."
# Get the absolute path of the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
DIR_NAME="$(basename "$SCRIPT_DIR")"

echo "Finalizing cleanup. The folder $DIR_NAME will be deleted."
cd "$PARENT_DIR"
rm -rf "$SCRIPT_DIR"

echo ""
echo "============================================================"
echo "   Uninstall Complete!"
echo "============================================================"
echo ""
