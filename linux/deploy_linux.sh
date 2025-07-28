#!/bin/bash

# Kerala Radar Scraper - Production Deployment Script for Linux
# This script sets up the radar scraper as a system service

set -e  # Exit on any error

echo "🚀 Kerala Radar Scraper - Production Deployment"
echo "=============================================="

# Get the parent directory (where the main scripts are)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
INSTALL_DIR="/opt/radar-scraper"
SERVICE_USER="radar"
SERVICE_GROUP="radar"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root for system installation"
   echo "   Run: sudo ./linux/deploy_linux.sh"
   exit 1
fi

echo "✅ Running as root - proceeding with system installation"

# Install system dependencies
echo "📦 Installing system dependencies..."
if command -v apt &> /dev/null; then
    # Ubuntu/Debian
    apt update
    apt install -y python3 python3-pip python3-venv curl wget systemd
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum install -y python3 python3-pip curl wget systemd
elif command -v dnf &> /dev/null; then
    # Fedora
    dnf install -y python3 python3-pip curl wget systemd
else
    echo "❌ Unsupported package manager. Please install manually:"
    echo "   - python3, python3-pip, python3-venv, curl, wget, systemd"
    exit 1
fi

# Create service user
echo "👤 Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --home-dir $INSTALL_DIR --shell /bin/false --user-group $SERVICE_USER
    echo "   ✅ Created user: $SERVICE_USER"
else
    echo "   ✅ User already exists: $SERVICE_USER"
fi

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/radar_images/{caz,ppz,ppi,zdr,vp2,3ds,kochi}

# Copy files to installation directory
echo "📄 Copying application files..."
cd "$PARENT_DIR"
cp radar_scraper.py mosdac_only.py requirements.txt $INSTALL_DIR/
cp linux/run_radar_linux.sh $INSTALL_DIR/
chmod +x $INSTALL_DIR/radar_scraper.py
chmod +x $INSTALL_DIR/run_radar_linux.sh

# Set up virtual environment
echo "🐍 Setting up Python virtual environment..."
cd $INSTALL_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install requests

# Set ownership
echo "🔐 Setting file ownership..."
chown -R $SERVICE_USER:$SERVICE_GROUP $INSTALL_DIR

# Install systemd service files
echo "⚙️  Installing systemd service..."
cp "$PARENT_DIR/linux/radar-scraper.service" /etc/systemd/system/
cp "$PARENT_DIR/linux/radar-scraper.timer" /etc/systemd/system/

# Update service file with correct paths
sed -i "s|/opt/radar-scraper|$INSTALL_DIR|g" /etc/systemd/system/radar-scraper.service
sed -i "s|User=radar|User=$SERVICE_USER|g" /etc/systemd/system/radar-scraper.service
sed -i "s|Group=radar|Group=$SERVICE_GROUP|g" /etc/systemd/system/radar-scraper.service

# Reload systemd and enable services
echo "🔄 Enabling systemd services..."
systemctl daemon-reload
systemctl enable radar-scraper.service
systemctl enable radar-scraper.timer

# Test the installation
echo "🧪 Testing installation..."
cd $INSTALL_DIR
sudo -u $SERVICE_USER $INSTALL_DIR/venv/bin/python $INSTALL_DIR/radar_scraper.py --help > /dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Installation test passed"
else
    echo "   ❌ Installation test failed"
    exit 1
fi

# Start the timer
echo "▶️  Starting radar scraper timer..."
systemctl start radar-scraper.timer

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Installation Summary:"
echo "   📁 Installation directory: $INSTALL_DIR"
echo "   👤 Service user: $SERVICE_USER"
echo "   ⏰ Timer: Every 10 minutes"
echo "   📊 Images saved to: $INSTALL_DIR/radar_images/"
echo ""
echo "🛠️  Management commands:"
echo "   Status:     systemctl status radar-scraper.timer"
echo "   Start:      systemctl start radar-scraper.timer"
echo "   Stop:       systemctl stop radar-scraper.timer"
echo "   Logs:       journalctl -u radar-scraper.service -f"
echo "   Manual run: sudo -u $SERVICE_USER $INSTALL_DIR/run_radar_linux.sh"
echo ""
echo "🔧 Configuration files:"
echo "   Service: /etc/systemd/system/radar-scraper.service"
echo "   Timer:   /etc/systemd/system/radar-scraper.timer"
echo ""
echo "📈 Monitor with:"
echo "   systemctl list-timers radar-scraper.timer"
echo "   journalctl -u radar-scraper.service --since '1 hour ago'"
