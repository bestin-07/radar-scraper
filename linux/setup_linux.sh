#!/bin/bash

# Kerala Radar Scraper - Linux Setup Script
# This script sets up the radar scraper on a Linux system

set -e  # Exit on any error

echo "🐧 Kerala Radar Scraper - Linux Setup"
echo "======================================"

# Get the parent directory (where the main scripts are)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PARENT_DIR"

echo "📁 Working in: $(pwd)"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first:"
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "   Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Check if version is 3.8+
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.8+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📋 Installing Python dependencies..."
pip install requests

# Make the main script executable
echo "🔧 Making scripts executable..."
chmod +x radar_scraper.py
chmod +x linux/run_radar_linux.sh

# Create directories
echo "📁 Creating radar image directories..."
mkdir -p radar_images/{caz,ppz,ppi,zdr,vp2,3ds,maxz}

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 How to run:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Run the scraper: ./radar_scraper.py"
echo "   3. Or use the convenience script: ./linux/run_radar_linux.sh"
echo ""
echo "📁 Downloaded images will be saved to:"
echo "   - Radar data: radar_images/{caz,ppz,ppi,zdr,vp2,3ds,maxz}/"
echo ""
echo "⏰ To run automatically, add to crontab:"
echo "   # Run every 10 minutes"
echo "   */10 * * * * cd $(pwd) && source venv/bin/activate && ./radar_scraper.py"
