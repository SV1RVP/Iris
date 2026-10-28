#!/bin/bash
# Iris Meteo Beacon - Linux Universal Installation Script
# Author: Alexandros - Ermis Tsourapas, SV1RVP

echo ""
echo "============================================================"
echo "      Iris Meteo Beacon - Universal Linux Installer"
echo "============================================================"
echo ""

# Detect Distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS=$(uname -s)
fi

echo "Detected OS: $OS"
echo "Installing system dependencies..."

case $OS in
    ubuntu|debian|raspbian)
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv libsdl2-mixer-2.0-0
        ;;
    fedora)
        sudo dnf update -y
        sudo dnf install -y python3 python3-pip SDL2_mixer
        ;;
    centos|rhel|almalinux|rocky)
        sudo dnf install -y epel-release
        sudo dnf update -y
        sudo dnf install -y python3 python3-pip SDL2_mixer
        ;;
    arch)
        sudo pacman -Syu --noconfirm python python-pip sdl2_mixer
        ;;
    opensuse*|suse)
        sudo zypper refresh
        sudo zypper install -y python3 python3-pip python3-virtualenv SDL2_mixer
        ;;
    alpine)
        sudo apk update
        sudo apk add python3 py3-pip sdl2_mixer
        ;;
    *)
        echo "[WARNING] Unknown distribution: $OS"
        echo "Please make sure python3, pip, and SDL2_mixer are installed manually."
        ;;
esac

# Create virtual environment
echo ""
echo "Setting up Python virtual environment (.venv)..."
python3 -m venv .venv
source .venv/bin/activate

# Install Python requirements
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
SERVICE_FILE="/etc/systemd/system/iris-meteo.service"
CURRENT_DIR=$(pwd)
USER=$(whoami)

echo ""
echo "Creating systemd service at $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE << EOF
[Unit]
Description=Iris Meteo Beacon Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/.venv/bin/python $CURRENT_DIR/main.py
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=iris-meteo

[Install]
WantedBy=multi-user.target
EOF"

echo "Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable iris-meteo.service
sudo systemctl start iris-meteo.service

# Final group check for PTT
echo ""
echo "Checking Serial permissions..."
if [[ "$OS" == "arch" || "$OS" == "fedora" || "$OS" == "centos" || "$OS" == "rhel" ]]; then
    GROUP="uucp"
else
    GROUP="dialout"
fi

if ! groups $USER | grep -q $GROUP; then
    echo "[TIP] To use Serial PTT, your user needs to be in the '$GROUP' group."
    echo "      Run: sudo usermod -a -G $GROUP $USER"
    echo "      (Note: You will need to log out and back in for changes to take effect)"
fi

echo ""
echo "============================================================"
echo "   Installation Complete! v1.1.2"
echo "============================================================"
echo "The Iris Meteo Beacon is now running in the background."
echo "View logs: sudo journalctl -u iris-meteo -f"
echo "Access Dashboard: http://localhost:1982"
echo ""
