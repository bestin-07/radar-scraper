#!/bin/bash

# Kerala Radar Scraper - Linux Runner Script
# Convenience script to run the radar scraper with proper environment

# Get the parent directory (where the main scripts are)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PARENT_DIR"

echo "🌦️  Kerala Radar Scraper - Linux"
echo "================================="
echo "📁 Working in: $(pwd)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run setup first:"
    echo "   chmod +x linux/setup_linux.sh && ./linux/setup_linux.sh"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Run the radar scraper
echo "🚀 Starting radar scraper..."
echo "   Command: python3 radar_scraper.py"
echo ""

python3 radar_scraper.py

echo ""
echo "✅ Radar scraper completed!"
echo "📁 Check radar_images/ directories for downloaded files"
