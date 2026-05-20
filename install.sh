#!/bin/bash
# Installation script for the water meter pulse counter service
# Run on your Raspberry Pi as root (or with sudo)

set -e

INSTALL_DIR="/opt/water-meter"
STATE_DIR="/var/lib/water-meter"
SERVICE_USER="water-meter"

echo "=== Water Meter Pulse Counter - Installation ==="
echo ""

# Create service user (no login, member of gpio group)
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating service user: $SERVICE_USER"
    useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"
    usermod -aG gpio "$SERVICE_USER"
else
    echo "User $SERVICE_USER already exists"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --quiet gpiod paho-mqtt

# Create directories
echo "Setting up directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$STATE_DIR"
chown "$SERVICE_USER:gpio" "$STATE_DIR"

# Copy files
echo "Installing files..."
cp water_meter.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/water_meter.py"

# Install systemd service
echo "Installing systemd service..."
cp water-meter.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable water-meter

echo ""
echo "=== Installation complete ==="
echo ""
echo "Before starting, edit the service environment if needed:"
echo "  sudo systemctl edit water-meter"
echo ""
echo "Then start the service:"
echo "  sudo systemctl start water-meter"
echo ""
echo "Check status:"
echo "  sudo systemctl status water-meter"
echo "  journalctl -u water-meter -f"
